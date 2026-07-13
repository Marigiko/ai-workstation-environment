#!/usr/bin/env python3
"""Telegram Bot for AI Engineering Platform."""

import os
import json
import logging
import asyncio
from pathlib import Path
from typing import Optional, Dict
from datetime import datetime

import aiohttp
from telegram import Update, BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

from components.telegram_bot.project_manager import ProjectManager

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


class TelegramBot:
    """Telegram bot for AI Engineering platform."""

    def __init__(self, config_path: str = None):
        self.config = self._load_config(config_path)
        self.sessions: Dict[str, dict] = {}
        self.proxy_url = self.config["proxy"]["api_url"]
        self.litellm_url = self.config["litellm"]["api_url"]
        self.litellm_api_key = self.config["litellm"]["api_key"]
        self.n8n_url = self.config["n8n"]["webhook_url"]
        self.project_manager = ProjectManager()

    def _load_config(self, config_path: str = None) -> dict:
        if config_path and Path(config_path).exists():
            import yaml
            with open(config_path) as f:
                return yaml.safe_load(f)
        return {
            "bot": {"token": os.getenv("TELEGRAM_BOT_TOKEN", ""), "allowed_users": []},
            "proxy": {"api_url": "http://localhost:8090"},
            "litellm": {"api_url": "http://localhost:4000", "api_key": os.environ.get("LITELLM_API_KEY", "")},
            "n8n": {"webhook_url": "http://localhost:5678/webhook/telegram"},
        }

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command."""
        # Show current project if selected
        project = self.project_manager.get_current_project()
        project_info = ""
        if project:
            project_info = f"\n📁 Proyecto actual: {project['name']} ({project['branch']})\n"

        await update.message.reply_text(
            "🤖 AI Engineering Bot\n"
            f"{project_info}\n"
            "📌 Proyecto:\n"
            "  /projects — Ver proyectos\n"
            "  /project <nombre> — Seleccionar proyecto\n"
            "  /branch <rama> — Cambiar rama\n"
            "  /newbranch <rama> — Crear rama\n"
            "  /gitstatus — Estado git\n\n"
            "📋 Trabajo:\n"
            "  /prompt <texto> — Enviar tarea\n"
            "  /session — Gestionar sesiones\n"
            "  /worktree — Gestionar worktrees\n"
            "  /commit <mensaje> — Git commit\n\n"
            "🤖 Modelo:\n"
            "  /models — Listar modelos\n"
            "  /model <nombre> — Cambiar modelo\n"
            "  /agent <nombre> — Cambiar agente\n"
            "  /auto — Modo automatico\n\n"
            "📊 Sistema:\n"
            "  /status — Estado del sistema"
        )

    async def prompt(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /prompt command - send to AI with Headroom compression."""
        if not context.args:
            await update.message.reply_text(
                "Uso: /prompt <descripcion>\n\n"
                "Ejemplo: /prompt escribe una funcion fibonacci"
            )
            return

        task_text = " ".join(context.args)
        user_id = str(update.effective_user.id)

        # Get user's preferred model (default: claude for agent capabilities)
        model = self.sessions.get(user_id, {}).get("model", "claude")

        # Show typing indicator
        await update.message.chat.send_action("typing")

        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "model": model,
                    "messages": [{"role": "user", "content": task_text}],
                    "max_tokens": 1024,
                    "headroom": True,
                }

                async with session.post(
                    f"{self.proxy_url}/v1/chat/completions",
                    json=payload,
                    timeout=180
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        content = data["choices"][0]["message"]["content"]
                        usage = data.get("usage", {})

                        # Format response
                        response = f"🤖 Respuesta ({model}):\n\n{content}"

                        # Add compression stats
                        orig = usage.get("original_tokens", 0)
                        comp = usage.get("compressed_tokens", 0)
                        if orig > 0:
                            savings = (1 - comp/orig) * 100 if comp < orig else 0
                            response += f"\n\n📊 Tokens: {orig} → {comp} (ahorro: {savings:.0f}%)"

                        await update.message.reply_text(response)
                    else:
                        error = await resp.text()
                        await update.message.reply_text(f"Error: {resp.status}\n{error[:200]}")
        except asyncio.TimeoutError:
            await update.message.reply_text("⏱ Timeout - el modelo tardó demasiado")
        except Exception as e:
            logger.error(f"Error sending prompt: {e}")
            await update.message.reply_text(f"Error: {str(e)}")

    async def status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command."""
        try:
            async with aiohttp.ClientSession() as session:
                # Check AI Proxy
                try:
                    async with session.get(f"{self.proxy_url}/health", timeout=5) as resp:
                        proxy_ok = resp.status == 200
                        proxy_data = await resp.json() if proxy_ok else {}
                except:
                    proxy_ok = False
                    proxy_data = {}

                # Check LiteLLM
                try:
                    async with session.get(
                        f"{self.litellm_url}/health",
                        headers={"Authorization": f"Bearer {self.litellm_api_key}"},
                        timeout=5
                    ) as resp:
                        litellm_ok = resp.status == 200
                except:
                    litellm_ok = False

                # Check Ollama
                try:
                    async with session.get("http://localhost:11434/api/tags", timeout=5) as resp:
                        ollama_ok = resp.status == 200
                        ollama_data = await resp.json() if ollama_ok else {}
                        ollama_models = len(ollama_data.get("models", []))
                except:
                    ollama_ok = False
                    ollama_models = 0

                # Check n8n
                try:
                    async with session.get("http://localhost:5678/healthz", timeout=5) as resp:
                        n8n_ok = resp.status == 200
                except:
                    n8n_ok = False

                status_text = (
                    f"📊 Estado del Sistema\n\n"
                    f"AI Proxy (8090): {'✅' if proxy_ok else '❌'}\n"
                    f"LiteLLM (4000): {'✅' if litellm_ok else '❌'}\n"
                    f"Ollama (11434): {'✅' if ollama_ok else '❌'} ({ollama_models} modelos)\n"
                    f"n8n (5678): {'✅' if n8n_ok else '❌'}\n"
                    f"\nHeadroom: ✅ Activo"
                )
                await update.message.reply_text(status_text)
        except Exception as e:
            await update.message.reply_text(f"Error al verificar estado: {str(e)}")

    async def approve(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /approve command."""
        if not context.args:
            await update.message.reply_text("Uso: /approve <task_id>")
            return

        task_id = context.args[0]
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.workspace_url}/tasks/{task_id}/approve", timeout=10
                ) as resp:
                    if resp.status == 200:
                        await update.message.reply_text(f"✅ Tarea {task_id} aprobada")
                    else:
                        await update.message.reply_text(f"Error: {resp.status}")
        except Exception as e:
            await update.message.reply_text(f"Error: {str(e)}")

    async def reject(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /reject command."""
        if not context.args:
            await update.message.reply_text("Uso: /reject <task_id>")
            return

        task_id = context.args[0]
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.workspace_url}/tasks/{task_id}/reject", timeout=10
                ) as resp:
                    if resp.status == 200:
                        await update.message.reply_text(f"❌ Tarea {task_id} rechazada")
                    else:
                        await update.message.reply_text(f"Error: {resp.status}")
        except Exception as e:
            await update.message.reply_text(f"Error: {str(e)}")

    async def models(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /models command."""
        try:
            async with aiohttp.ClientSession() as session:
                # Get models from AI Proxy
                async with session.get(
                    f"{self.proxy_url}/v1/models", timeout=10
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        proxy_models = [m["id"] for m in data.get("data", [])]
                    else:
                        proxy_models = []

                # Get models from LiteLLM
                try:
                    async with session.get(
                        f"{self.litellm_url}/v1/models",
                        headers={"Authorization": f"Bearer {self.litellm_api_key}"},
                        timeout=10
                    ) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            litellm_models = [m["id"] for m in data.get("data", [])]
                        else:
                            litellm_models = []
                except:
                    litellm_models = []

                models_text = "🤖 Modelos Disponibles\n\n"

                if proxy_models:
                    models_text += "📡 Via AI Proxy (Headroom compression):\n"
                    for m in proxy_models:
                        models_text += f"  • {m}\n"
                    models_text += "\n"

                if litellm_models:
                    models_text += "🔗 Via LiteLLM:\n"
                    for m in litellm_models[:10]:  # Limit to 10
                        models_text += f"  • {m}\n"
                    if len(litellm_models) > 10:
                        models_text += f"  ... y {len(litellm_models) - 10} más\n"

                await update.message.reply_text(models_text)
        except Exception as e:
            await update.message.reply_text(f"Error: {str(e)}")

    async def worktrees(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /worktrees command."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.workspace_url}/workspaces", timeout=10
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        worktrees = data if isinstance(data, list) else data.get("data", [])
                        if worktrees:
                            wt_text = "\n".join(
                                [f"  • {wt.get('name', 'N/A')} ({wt.get('id', '')[:8]})" for wt in worktrees]
                            )
                        else:
                            wt_text = "  No hay worktrees"
                        await update.message.reply_text(
                            f"📁 Worktrees\n\n{wt_text}"
                        )
                    else:
                        await update.message.reply_text("Error al listar worktrees")
        except Exception as e:
            await update.message.reply_text(f"Error: {str(e)}")

    async def commit(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /commit command - git commit."""
        if not context.args:
            await update.message.reply_text("Uso: /commit <mensaje>")
            return

        message = " ".join(context.args)
        try:
            async with aiohttp.ClientSession() as session:
                # Execute git commit via workspace API
                async with session.post(
                    f"{self.workspace_url}/tasks",
                    json={
                        "workspace_id": "default",
                        "title": f"Git commit: {message}",
                        "description": f"Execute: git commit -m '{message}'",
                        "priority": 1,
                    },
                    timeout=10,
                ) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        await update.message.reply_text(
                            f"📝 Commit enviado\\n"
                            f"Mensaje: {message}\\n"
                            f"Estado: Pendiente de ejecucion"
                        )
                    else:
                        await update.message.reply_text(f"Error: {resp.status}")
        except Exception as e:
            await update.message.reply_text(f"Error: {str(e)}")

    async def model(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /model command - switch model."""
        if not context.args:
            await update.message.reply_text("Uso: /model <nombre_del_modelo>")
            return

        model_name = context.args[0]
        user_id = str(update.effective_user.id)
        if user_id not in self.sessions:
            self.sessions[user_id] = {}

        self.sessions[user_id]["model"] = model_name
        await update.message.reply_text(f"🤖 Modelo cambiado a: {model_name}")

    async def agent(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /agent command - switch agent."""
        if not context.args:
            await update.message.reply_text(
                "Uso: /agent <nombre>\\n\\n"
                "Agentes disponibles:\\n"
                "  • coder - Desarrollo de codigo\\n"
                "  • reviewer - Revision de codigo\\n"
                "  • documenter - Documentacion\\n"
                "  • tester - Testing\\n"
                "  • debugger - Debugging\\n"
                "  • architect - Arquitectura"
            )
            return

        agent_name = context.args[0]
        user_id = str(update.effective_user.id)
        if user_id not in self.sessions:
            self.sessions[user_id] = {}

        self.sessions[user_id]["agent"] = agent_name
        await update.message.reply_text(f"🤖 Agente cambiado a: {agent_name}")

    async def auto_mode(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /auto command - toggle auto mode."""
        user_id = str(update.effective_user.id)
        if user_id not in self.sessions:
            self.sessions[user_id] = {"auto_mode": False}
        
        self.sessions[user_id]["auto_mode"] = not self.sessions[user_id]["auto_mode"]
        mode = "ACTIVADO" if self.sessions[user_id]["auto_mode"] else "DESACTIVADO"
        await update.message.reply_text(f"🤖 Modo Automatico: {mode}")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular messages."""
        user_id = str(update.effective_user.id)
        text = update.message.text

        # Check if auto mode is enabled
        if user_id in self.sessions and self.sessions[user_id].get("auto_mode"):
            # Auto mode: send directly to orchestrator
            await self.prompt(update, context)
        else:
            await update.message.reply_text(
                "Usa /prompt <descripcion> para enviar una tarea.\n"
                "O /auto para activar modo automatico."
            )

    # ============================================
    # Project Management Commands
    # ============================================

    async def list_projects(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /projects command."""
        projects = self.project_manager.list_projects()

        if not projects:
            await update.message.reply_text("No se encontraron proyectos en /mnt/d/Projects/")
            return

        # Group by type
        git_projects = [p for p in projects if p["is_git"]]
        other_projects = [p for p in projects if not p["is_git"]]

        msg = "📁 Proyectos en D:\\Projects\\\n\n"

        if git_projects:
            msg += "🔧 Con Git:\n"
            for p in git_projects[:20]:  # Limit
                current = " ⭐" if p["name"] == self.project_manager.state.current_project else ""
                msg += f"  • {p['name']}{current}\n"
                msg += f"    Último acceso: {p['last_modified']}\n"
            if len(git_projects) > 20:
                msg += f"  ... y {len(git_projects) - 20} más\n"
            msg += "\n"

        if other_projects:
            msg += "📂 Otros:\n"
            for p in other_projects[:10]:
                msg += f"  • {p['name']}\n"
            if len(other_projects) > 10:
                msg += f"  ... y {len(other_projects) - 10} más\n"

        msg += "\n Usa /project <nombre> para trabajar en un proyecto"

        await update.message.reply_text(msg)

    async def select_project(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /project command."""
        if not context.args:
            current = self.project_manager.get_current_project()
            if current:
                await update.message.reply_text(
                    f"📁 Proyecto actual: {current['name']}\n"
                    f"Rama: {current['branch']}\n\n"
                    f"Usa /project <nombre> para cambiar"
                )
            else:
                await update.message.reply_text(
                    "Uso: /project <nombre> [rama]\n\n"
                    "Ejemplo:\n"
                    "  /project ai-workstation\n"
                    "  /project ai-workstation main"
                )
            return

        project_name = context.args[0]
        branch = context.args[1] if len(context.args) > 1 else None

        result = self.project_manager.select_project(project_name)
        if not result:
            await update.message.reply_text(f"❌ Proyecto no encontrado: {project_name}")
            return

        # Select branch if provided
        if branch:
            self.project_manager.select_branch(branch, project_name)
            result["branch"] = branch

        msg = f"✅ Proyecto seleccionado: {result['name']}\n\n"
        msg += f"📍 Ruta: {result['path']}\n"
        msg += f"🌿 Rama: {result['branch']}\n"

        if result["branches"]:
            msg += f"\n📋 Ramas disponibles ({len(result['branches'])}):\n"
            for b in result["branches"][:10]:
                marker = " → " if b == result["branch"] else "   "
                msg += f"{marker}{b}\n"
            if len(result["branches"]) > 10:
                msg += f"   ... y {len(result['branches']) - 10} más\n"

        msg += "\n📌 Comandos disponibles:\n"
        msg += "  /branch <rama> — Cambiar rama\n"
        msg += "  /gitstatus — Ver estado git\n"
        msg += "  /session — Gestionar sesiones\n"
        msg += "  /worktree — Gestionar worktrees\n"
        msg += "  /prompt <tarea> — Enviar tarea"

        await update.message.reply_text(msg)

    async def select_branch(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /branch command."""
        if not context.args:
            # List branches
            project = self.project_manager.get_current_project()
            if not project:
                await update.message.reply_text("Primero selecciona un proyecto: /project <nombre>")
                return

            branches = self.project_manager.list_branches()
            msg = f"🌿 Ramas de {project['name']}:\n\n"
            for b in branches:
                marker = " → " if b == project["branch"] else "   "
                msg += f"{marker}{b}\n"
            msg += "\nUsa /branch <rama> para cambiar"
            await update.message.reply_text(msg)
            return

        branch = context.args[0]
        if self.project_manager.select_branch(branch):
            await update.message.reply_text(f"✅ Rama cambiada a: {branch}")
        else:
            await update.message.reply_text(f"❌ Error al cambiar rama: {branch}")

    async def create_branch(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /newbranch command."""
        if not context.args:
            await update.message.reply_text("Uso: /newbranch <nombre-rama>")
            return

        branch = context.args[0]
        if self.project_manager.create_branch(branch):
            await update.message.reply_text(f"✅ Rama creada y seleccionada: {branch}")
        else:
            await update.message.reply_text(f"❌ Error al crear rama: {branch}")

    async def git_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /gitstatus command."""
        status = self.project_manager.get_git_status()

        if "error" in status:
            await update.message.reply_text(f"❌ {status['error']}")
            return

        msg = f"📊 Estado Git\n\n"
        msg += f"🌿 Rama: {status['branch']}\n"
        msg += f"📝 Archivos modificados: {status['changed_files']}\n"

        if status["recent_commits"]:
            msg += f"\n📋 Últimos commits:\n"
            for commit in status["recent_commits"][:5]:
                msg += f"  • {commit}\n"

        await update.message.reply_text(msg)

    async def session_cmd(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /session command."""
        project = self.project_manager.get_current_project()
        if not project:
            await update.message.reply_text("Primero selecciona un proyecto: /project <nombre>")
            return

        if not context.args:
            # List sessions
            sessions = self.project_manager.list_sessions()
            msg = f"📋 Sesiones de {project['name']}:\n\n"

            if sessions:
                for s in sessions:
                    status_icon = "🟢" if s["status"] == "active" else "⚪"
                    msg += f"{status_icon} {s['id']}: {s['title']}\n"
                    msg += f"   Rama: {s.get('branch', 'N/A')}\n"
                    msg += f"   Creada: {s['created_at'][:16]}\n\n"
            else:
                msg += "No hay sesiones\n\n"

            msg += "📌 Comandos:\n"
            msg += "  /session new <titulo> — Crear sesión\n"
            msg += "  /session <id> — Ver detalles"
            await update.message.reply_text(msg)
            return

        if context.args[0] == "new":
            title = " ".join(context.args[1:]) if len(context.args) > 1 else "Sin título"
            session = self.project_manager.create_session(title)
            await update.message.reply_text(
                f"✅ Sesión creada\n"
                f"ID: {session['id']}\n"
                f"Título: {session['title']}\n"
                f"Rama: {session.get('branch', 'N/A')}"
            )
        else:
            # Show session details
            session_id = context.args[0]
            sessions = self.project_manager.list_sessions()
            session = next((s for s in sessions if s["id"] == session_id), None)
            if session:
                msg = f"📋 Sesión {session['id']}\n\n"
                msg += f"Título: {session['title']}\n"
                msg += f"Estado: {session['status']}\n"
                msg += f"Rama: {session.get('branch', 'N/A')}\n"
                msg += f"Creada: {session['created_at']}\n"
                await update.message.reply_text(msg)
            else:
                await update.message.reply_text(f"❌ Sesión no encontrada: {session_id}")

    async def worktree_cmd(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /worktree command."""
        project = self.project_manager.get_current_project()
        if not project:
            await update.message.reply_text("Primero selecciona un proyecto: /project <nombre>")
            return

        if not context.args:
            # List worktrees
            worktrees = self.project_manager.list_worktrees()
            msg = f"🌳 Worktrees de {project['name']}:\n\n"

            if worktrees:
                for wt in worktrees:
                    msg += f"  • {wt.get('path', 'N/A')}\n"
                    if "branch" in wt:
                        msg += f"    Rama: {wt['branch']}\n"
                    if "head" in wt:
                        msg += f"    HEAD: {wt['head'][:8]}\n"
            else:
                msg += "No hay worktrees\n\n"

            msg += "\n📌 Comandos:\n"
            msg += "  /worktree new <rama> — Crear worktree\n"
            msg += "  /worktree list — Listar worktrees"
            await update.message.reply_text(msg)
            return

        if context.args[0] == "new":
            if len(context.args) < 2:
                await update.message.reply_text("Uso: /worktree new <nombre-rama>")
                return

            branch = context.args[1]
            result = self.project_manager.create_worktree(branch)

            if "error" in result:
                await update.message.reply_text(f"❌ Error: {result['error']}")
            else:
                await update.message.reply_text(
                    f"✅ Worktree creado\n"
                    f"Rama: {branch}\n"
                    f"Ruta: {result['path']}"
                )
        else:
            await update.message.reply_text(
                "Uso:\n"
                "  /worktree — Listar worktrees\n"
                "  /worktree new <rama> — Crear worktree"
            )

    async def notify(self, bot, chat_id: int, message: str):
        """Send notification to user."""
        try:
            await bot.send_message(chat_id=chat_id, text=message)
        except Exception as e:
            logger.error(f"Error sending notification: {e}")

    def run(self):
        """Run the bot."""
        token = self.config["bot"]["token"]
        if not token:
            logger.error("No Telegram bot token configured!")
            return

        app = Application.builder().token(token).build()

        # Register handlers
        app.add_handler(CommandHandler("start", self.start))
        app.add_handler(CommandHandler("help", self.start))
        app.add_handler(CommandHandler("prompt", self.prompt))
        app.add_handler(CommandHandler("status", self.status))
        app.add_handler(CommandHandler("approve", self.approve))
        app.add_handler(CommandHandler("reject", self.reject))
        app.add_handler(CommandHandler("models", self.models))
        app.add_handler(CommandHandler("commit", self.commit))
        app.add_handler(CommandHandler("model", self.model))
        app.add_handler(CommandHandler("agent", self.agent))
        app.add_handler(CommandHandler("auto", self.auto_mode))

        # Project management handlers
        app.add_handler(CommandHandler("projects", self.list_projects))
        app.add_handler(CommandHandler("project", self.select_project))
        app.add_handler(CommandHandler("branch", self.select_branch))
        app.add_handler(CommandHandler("newbranch", self.create_branch))
        app.add_handler(CommandHandler("gitstatus", self.git_status))
        app.add_handler(CommandHandler("session", self.session_cmd))
        app.add_handler(CommandHandler("worktree", self.worktree_cmd))

        app.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)
        )

        logger.info("Bot started - Listening for messages...")

        # Run with drop_pending_updates to avoid processing old messages
        app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    bot = TelegramBot()
    bot.run()