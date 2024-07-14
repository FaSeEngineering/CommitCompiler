
$name = Read-Host "Docker Repository"
$version = Read-Host "Version Tag (e.g: 1.0.4)"
$image = "${name}:${version}"
Write-Output "Building Image: $image"
docker build -t $image .
docker tag $image "${name}:latest"
Write-Output "Uploading Image:`n - $image`n - ${name}:latest"
docker push $image
docker push "${name}:latest"
Write-Output "Build complete."