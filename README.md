# Stock Manager

Stock Manager is a Django web app for managing stock across warehouses and stores. Each storage space has a grid of bins, so you can see where products are kept, how much space they use, and where there is room for more.

You can receive stock, move it between positions, and remove items when they leave inventory. The app does not include user accounts or require Django admin for everyday use.

## Features

- Dashboard with storage-space, product, and item counts, plus recent transfers.
- Product and storage-space management, including editing and deletion with confirmation.
- Automatic bin creation when a storage space is added.
- Individual bin capacities and colour-coded capacity bars.
- Product categories, search by name or SKU, filtering, and sorting.
- Receiving, transferring, and removing stock from the storage map or separate pages.
- Transfer history with links to the products and positions involved.
- Validation to prevent overfilled bins and invalid stock movements.
- Responsive layouts and a custom 404 page.

## Technology

The app uses Python, Django, SQLite, Django templates, CSS, and SVG assets. Package versions are listed in `requirements.txt`.

It was developed using Python 3.14.6 on macOS. You need Python, pip, and Git to follow the setup below. There is no Node.js setup or separate database server to install.

## Run locally

```sh
git clone https://github.com/FuewI/stock-manager.git
cd stock-manager
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

On Windows, activate the virtual environment in PowerShell with:

```powershell
.venv\Scripts\Activate.ps1
```

Open http://127.0.0.1:8000/ in your browser. Press `Ctrl+C` in the terminal to stop the server.

To run the app again later, open a terminal in the project folder, activate `.venv`, and run `python manage.py runserver`.

### Local settings

The default configuration uses `config.settings` and creates `db.sqlite3` in the project folder. No environment variables, API credentials, superuser, or demo data are needed for local use.

These are development settings: `DEBUG=True` and the included development secret key are not suitable for a public deployment. The custom 404 page appears when `DEBUG=False`; otherwise, Django shows its technical error page.

## Getting started

A fresh database starts empty. Create your first records through the website:

1. Add a category from **Categories**, if needed.
2. Create a product with a unique SKU and a positive space-per-item value.
3. Create a warehouse or store. Choose its grid dimensions and default bin capacity. The app creates the bins automatically.
4. Open the storage map, select an empty position, and use **Receive stock** to add a product and quantity.
5. Use **Move stock** to transfer items to another compatible position. You need at least two bins for a transfer.
6. Check **Transfer history** to see the recorded movement.

Use **Remove stock** when items leave inventory. To change one bin's capacity, open **Full bin details → Edit capacity**.

Migrations create the database tables without adding sample records. Running migrations again does not clear existing data.

## How capacity works

Capacity uses abstract **storage units**, rather than physical measurements such as kilograms or cubic metres.

```text
Used capacity = quantity × space per item
Remaining capacity = bin capacity − used capacity
```

For example, a bin with a capacity of 100 can hold 25 items that each use 4 storage units.

Each bin holds one product type at a time. The same product can be stored in several bins. Receiving more stock into an occupied bin increases its quantity; the product selection is disabled. Empty the bin before storing a different product there.

A transfer destination must be empty or contain the same product, with enough capacity for the quantity being moved. Moving or removing all items leaves the source bin empty.

The app also prevents reducing a bin's capacity below its current use or changing a product's space requirement if that would overfill an existing bin. Grid dimensions and the default capacity are fixed after storage-space creation; individual bin capacities can still be edited.

### Deleting records

Products and storage spaces cannot be deleted while protected stock or transfer history refers to them. Deleting an unprotected storage space also deletes its bins.

Transfer history remains after stock has moved away, so an empty storage space may still be protected. There is no interface for deleting transfer history.

## Project structure

| Folder | Purpose |
| --- | --- |
| `config/` | Project settings and main URL configuration. |
| `storage/` | Warehouses, stores, bins, dashboard, shared templates, and static assets. |
| `products/` | Products, categories, search, filtering, and sorting. |
| `inventory/` | Stock quantities, receiving, removal, transfers, and history. |

### Models

| Model | Purpose |
| --- | --- |
| `StorageSpace` | A warehouse or store with grid dimensions and default bin capacity. |
| `StorageBin` | A position within a storage space, with its own capacity. |
| `Category` | A category that can be assigned to multiple products. |
| `Product` | Product details, a unique SKU, space per item, and categories. |
| `StockEntry` | A product and quantity stored in one bin. |
| `StockTransfer` | A recorded movement between two bins. |

A storage space has many bins. Products and categories have a many-to-many relationship. Each bin has at most one stock entry, while a product can have entries in multiple bins.

Pages share a base template and navigation. The storage map reuses a bin-card partial, and the `row_letter` template filter formats row numbers as letters.

## Optional demo data

Demo data uses a separate database, `demo.sqlite3`. With the virtual environment active, run:

```sh
python manage.py migrate --settings=config.settings_demo
python manage.py loaddata demo_data.json --settings=config.settings_demo
python manage.py runserver --settings=config.settings_demo
```

The fixture contains two categories, three products, two storage spaces, ten bins, six stock entries, and two example transfers. It includes empty, partially filled, and full bins.

Load it into an empty demo database. The fixture uses fixed IDs, so loading it again can overwrite matching records. It does not reset the database. Keep `--settings=config.settings_demo` on all demo commands to avoid loading it into your normal database.

To return to your normal database, stop the server and run:

```sh
python manage.py runserver
```

## Checks

```sh
python manage.py check
python manage.py makemigrations --check --dry-run
python -m pip check
python manage.py test
```

The current `tests.py` files are placeholders, so the test command does not provide automated regression coverage. Manually check stock operations, invalid quantities, capacity limits, protected deletion, and navigation before submitting changes.

## Limitations

- History records transfers only; receiving and removal do not create history records.
- Some protected-deletion messages refer to stock even when transfer history is what prevents deletion.
- Concurrent stock updates need further work. SQLite does not provide row locking through `select_for_update()`, and the current stock operations should not be treated as ready for simultaneous users.
- Very large grids can be slow to create and display. Product and transfer lists do not have pagination.
- Categories currently support creation and listing, rather than full editing and deletion.
- Authentication and production deployment configuration are outside the current scope.
