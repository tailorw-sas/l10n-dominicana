#!/usr/bin/env python3
import re

with open('models/account_move.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Corregir campo Binary si no está hecho
if 'attachment=True' not in content or 'l10n_do_ecf_edi_file' in content:
    # Ya debería estar corregido, pero verificamos
    pass

# 2. Añadir @api.depends al primer método
pattern1 = r'def _compute_l10n_do_enable_first_sequence\(self\):'
if pattern1 in content and '@api.depends' not in content[:content.find(pattern1)+100]:
    # Encontrar la posición y añadir
    pos = content.find(pattern1)
    new_content = content[:pos] + '    @api.depends("l10n_latam_document_type_id", "journal_id")\n' + content[pos:]
    content = new_content

# 3. Añadir @api.depends al segundo método
pattern2 = r'def _compute_is_ecf_invoice\(self\):'
if pattern2 in content and '@api.depends' not in content[:content.find(pattern2)+100]:
    pos = content.find(pattern2)
    new_content = content[:pos] + '    @api.depends("l10n_latam_document_type_id", "company_id")\n' + content[pos:]
    content = new_content

# Guardar
with open('models/account_move.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ account_move.py corregido para Odoo 18")
