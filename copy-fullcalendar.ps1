$sourceDir = "node_modules/@fullcalendar"
$targetDir = "static/plugins/fullcalendar/dist"

# Create target directory if it doesn't exist
New-Item -ItemType Directory -Force -Path $targetDir

# Copy core files
Copy-Item "$sourceDir/core/index.global.min.js" -Destination "$targetDir/core.min.js"
Copy-Item "$sourceDir/daygrid/index.global.min.js" -Destination "$targetDir/daygrid.min.js"
Copy-Item "$sourceDir/timegrid/index.global.min.js" -Destination "$targetDir/timegrid.min.js"
Copy-Item "$sourceDir/interaction/index.global.min.js" -Destination "$targetDir/interaction.min.js"
Copy-Item "$sourceDir/bootstrap5/index.global.min.js" -Destination "$targetDir/bootstrap5.min.js"

# Create locales directory and copy locales
New-Item -ItemType Directory -Force -Path "$targetDir/locales"
Copy-Item "$sourceDir/core/locales/*.global.min.js" -Destination "$targetDir/locales/"

# Rename locale files to remove .global from the name
Get-ChildItem "$targetDir/locales" -Filter "*.global.min.js" | ForEach-Object {
    $newName = $_.Name -replace '\.global\.min\.js$', '.min.js'
    Rename-Item $_.FullName $newName
}
