param([string]$Cmd)
# WMI-created processes live outside the ssh session's job object, so they survive the disconnect.
$py = "$env:LOCALAPPDATA\Programs\Python\Python312"
Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{
  CommandLine = "cmd /c set PATH=$py;$py\Scripts;%PATH% && cd /d D:\qwen-edit && $Cmd"
  CurrentDirectory = "D:\qwen-edit"
} | Select-Object ProcessId, ReturnValue | Format-List | Out-String
