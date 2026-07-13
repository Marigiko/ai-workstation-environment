' Launch Terax AI Workstation - invisible launcher (no black terminal window)
' Double-click this file or the .lnk shortcut to launch

Option Explicit

Dim ws, fso, wslDistro, gatewayUrl, maxWait, waited
Set ws = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

wslDistro = "Ubuntu-24.04"
gatewayUrl = "http://localhost:8000/health"
maxWait = 60

' Check if WSL is running
Dim wslCheck
Set wslCheck = ws.Exec("wsl.exe -d " & wslDistro -- " & "echo ok")
If wslCheck.StdOut.ReadLine() <> "ok" Then
    MsgBox "WSL is not running. Please start WSL first.", vbCritical, "AI Workstation"
    WScript.Quit 1
End If

' Check if gateway is already running
If Not CheckGateway() Then
    ' Start gateway
    ws.Run "wsl.exe -d " & wslDistro & " -- bash -c ""cd ~/ai-workstation && docker compose -f infrastructure/compose/docker-compose.prod.yml up -d""", 0, False
    
    ' Wait for gateway
    waited = 0
    Do While Not CheckGateway()
        WScript.Sleep 2000
        waited = waited + 2
        If waited >= maxWait Then
            MsgBox "Gateway did not start within " & maxWait & " seconds. Check WSL/Docker.", vbExclamation, "AI Workstation"
            WScript.Quit 1
        End If
    Loop
End If

' Launch Terax (WSLg will show GUI window)
ws.Run "wsl.exe -d " & wslDistro & " -- bash -c ""terax""", 0, False

WScript.Quit 0

Function CheckGateway()
    Dim http
    Set http = CreateObject("MSXML2.XMLHTTP")
    On Error Resume Next
    http.Open "GET", gatewayUrl, False
    http.Send
    If Err.Number = 0 And http.Status = 200 Then
        CheckGateway = True
    Else
        CheckGateway = False
    End If
    On Error GoTo 0
End Function
