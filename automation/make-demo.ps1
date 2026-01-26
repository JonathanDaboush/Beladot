# Seed demo data: users (all roles) + categories/subcategories, no products
# Also exports credentials to automation\demo-credentials.txt

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Write-Host "Bringing up containers..." -ForegroundColor Cyan
# Ensure services are up
docker compose up -d postgres backend

Write-Host "Seeding users (customers, sellers, CS, shipping, finance, managers)..." -ForegroundColor Cyan
docker compose exec backend python -m backend.scripts.seed_demo_data

Write-Host "Seeding categories & subcategories..." -ForegroundColor Cyan
docker compose exec backend python -m backend.scripts.seed_categories

Write-Host "Assigning images to users/categories/subcategories (if assets exist)..." -ForegroundColor Cyan
docker compose exec backend python -m backend.scripts.assign_images

Write-Host "Exporting demo credentials to automation\\demo-credentials.txt..." -ForegroundColor Cyan
# Save credentials to a host file for easy reuse
$credPath = Join-Path $PSScriptRoot 'demo-credentials.txt'
docker compose exec backend python -m backend.scripts.list_demo_credentials | Out-File -FilePath $credPath -Encoding UTF8
Write-Host "Saved: $credPath" -ForegroundColor Green

Write-Host "Summary counts (Postgres divina_dev)..." -ForegroundColor Cyan
# Use single-quoted SQL to avoid PowerShell escaping issues
$queries = @(
    "select count(*) as user_count from \"user\";",
    "select count(*) as category_count from category;",
    "select count(*) as subcategory_count from subcategory;",
    "select count(*) as product_count from product;"
)
foreach ($q in $queries) {
    docker compose exec postgres psql -U postgres -d divina_dev -c $q
}

Write-Host "Done." -ForegroundColor Green
