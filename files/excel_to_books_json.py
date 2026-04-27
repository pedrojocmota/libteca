"""
Converte ficheiros Excel do PNL para books.json (Django fixture)

Uso:
    1. Coloca os ficheiros Excel do PNL na mesma pasta que este script
    2. Edita a lista FILES em baixo com os nomes dos teus ficheiros
    3. Corre: python excel_to_books_json.py
    4. Copia o books.json gerado para library/fixtures/
    5. Corre: python manage.py loaddata books.json

Requisitos:
    pip install pandas openpyxl
"""

import pandas as pd
import json
import re
import os

# ── Configuração ──────────────────────────────────────────
# Adiciona aqui os ficheiros Excel que quiseres processar
FILES = [
    "Livros_selecionados_1semestre2024__1_.xlsx",
    "Livros_selecionados_2Semestre_2024_2.xlsx",
    "LivrosRecomendados_PNL_1S_2025.xlsx",
    "LivrosRecomendados_PNL_2S_2025.xlsx",
    # Adiciona futuros semestres aqui:
]
OUTPUT_FILE = "books.json"
# ─────────────────────────────────────────────────────────


def clean_title(title):
    """Remove prefixos como «Caro» ou <Os> dos títulos"""
    if pd.isna(title):
        return "Sem título"
    return re.sub(r'^[«<][^»>]+[»>]\s*', '', str(title)).strip()


def clean_author(author):
    """
    Limpa e formata o nome do autor:
    - Pega apenas o primeiro autor se houver vários (separados por ";")
    - Remove datas de nascimento/morte ex: ", 1951-" ou ", 1842-1891"
    - Converte "Apelido, Nome" → "Nome Apelido"
    - Evita nomes duplicados ex: "Platão, Platão" → "Platão"
    """
    if pd.isna(author):
        return "Autor desconhecido"
    author = str(author).split(';')[0].strip()
    author = re.sub(r',\s*\d{4}-?\d*\.?$', '', author).strip()
    if ',' in author:
        parts = author.split(',', 1)
        nome = parts[1].strip()
        apelido = parts[0].strip()
        if nome.lower() != apelido.lower():
            author = nome + ' ' + apelido
        else:
            author = apelido
    return author.strip()


def clean_isbn(isbn):
    """Remove hífens e espaços do ISBN"""
    if pd.isna(isbn):
        return ""
    return re.sub(r'[-\s]', '', str(isbn)).strip()


def main():
    print("=== Excel PNL → books.json ===\n")

    all_rows = []
    for f in FILES:
        if not os.path.exists(f):
            print(f"⚠️  Ficheiro não encontrado: {f} (a saltar)")
            continue
        df = pd.read_excel(f)
        all_rows.append(df[['ISBN', 'Título', 'Autor(es)']].copy())
        print(f"  ✅ {f}: {len(df)} livros")

    if not all_rows:
        print("\n❌ Nenhum ficheiro encontrado!")
        return

    combined = pd.concat(all_rows, ignore_index=True)
    total_before = len(combined)

    # Remove duplicados por ISBN
    combined['ISBN_clean'] = combined['ISBN'].apply(clean_isbn)
    combined = combined.drop_duplicates(subset='ISBN_clean', keep='first')

    # Remove duplicados por título (caso ISBN diferente mas título igual)
    combined['Título_clean'] = combined['Título'].apply(
        lambda x: str(x).lower().strip() if not pd.isna(x) else ''
    )
    combined = combined.drop_duplicates(subset='Título_clean', keep='first')

    total_after = len(combined)
    print(f"\n  Duplicados removidos: {total_before - total_after}")
    print(f"  Total final: {total_after} livros")

    # Gera o books.json
    books = []
    for pk, (_, row) in enumerate(combined.iterrows(), start=1):
        books.append({
            "model": "library.book",
            "pk": pk,
            "fields": {
                "title": clean_title(row['Título']),
                "author": clean_author(row['Autor(es)']),
                "cover_url": "",
                "available": True
            }
        })

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(books, f, ensure_ascii=False, indent=2)

    print(f"\n✅ {OUTPUT_FILE} gerado com {len(books)} livros!")
    print(f"\nAgora corre:")
    print(f"  python manage.py loaddata {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
