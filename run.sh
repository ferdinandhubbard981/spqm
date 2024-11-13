#!/bin/bash
set -e

. ../17/.venv/bin/activate

DB_NAME="spqm-db"
PORT=8069  # default port

for arg in "$@"; do
    case $arg in
        --dev)
            DB_NAME="spqm-db-dev"
            PORT=8070
            ;;
    esac
done

./../17/odoo/odoo-bin --addons-path="../17/odoo/addons/, ." -u spqm -d "$DB_NAME" -p "$PORT"
