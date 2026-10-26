$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$docxPath = Join-Path $scriptDir "EduVerse_AI_Project_Documentation.docx"
$pdfPath = Join-Path $scriptDir "EduVerse_AI_Project_Documentation.pdf"

Write-Output "Opening Word Application COM object..."
$word = New-Object -ComObject Word.Application
$word.Visible = $false

try {
    Write-Output "Opening DOCX: $docxPath"
    $doc = $word.Documents.Open($docxPath)
    Write-Output "Exporting to PDF: $pdfPath"
    # wdExportFormatPDF = 17
    $doc.ExportAsFixedFormat($pdfPath, 17)
    $doc.Close([ref]0) # 0 = wdDoNotSaveChanges
    Write-Output "SUCCESS: PDF generated successfully at $pdfPath"
}
catch {
    Write-Output "ERROR during PDF export: $($_.Exception.Message)"
}
finally {
    $word.Quit()
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($word) | Out-Null
    [System.GC]::Collect()
    [System.GC]::WaitForPendingFinalizers()
}
