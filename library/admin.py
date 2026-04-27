from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Book
import pandas as pd
import re

def clean_title(title):
    if pd.isna(title): return "Sem título"
    return re.sub(r'^[«<][^»>]+[»>]\s*', '', str(title)).strip()

def clean_author(author):
    if pd.isna(author): return "Autor desconhecido"
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
    if pd.isna(isbn): return ""
    return re.sub(r'[-\s]', '', str(isbn)).strip()

class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'available']
    search_fields = ['title', 'author']
    list_filter = ['available']

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-excel/', self.admin_site.admin_view(self.import_excel_view), name='library_book_import_excel'),
        ]
        return custom_urls + urls

    def import_excel_view(self, request):
        if request.method == 'POST' and request.FILES.get('excel_file'):
            excel_file = request.FILES['excel_file']

            try:
                df = pd.read_excel(excel_file)

                # Verifica se tem as colunas necessárias
                if 'ISBN' not in df.columns or 'Título' not in df.columns:
                    messages.error(request, "❌ Ficheiro inválido — precisa de colunas 'ISBN' e 'Título'.")
                    return redirect('..')

                added = 0
                skipped = 0

                for _, row in df.iterrows():
                    isbn = clean_isbn(row.get('ISBN'))
                    title = clean_title(row.get('Título'))
                    author = clean_author(row.get('Autor(es)', ''))

                    # Verifica duplicados por ISBN e título
                    if isbn and Book.objects.filter(title__iexact=title).exists():
                        skipped += 1
                        continue

                    Book.objects.create(
                        title=title,
                        author=author,
                        cover_url='',
                        available=True
                    )
                    added += 1

                messages.success(request, f"✅ {added} livros importados com sucesso! {skipped} duplicados ignorados.")
                return redirect('../')

            except Exception as e:
                messages.error(request, f"❌ Erro ao processar ficheiro: {str(e)}")
                return redirect('..')

        context = {
            **self.admin_site.each_context(request),
            'title': 'Importar Livros via Excel',
            'opts': self.model._meta,
        }
        return render(request, 'admin/import_excel.html', context)

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['import_url'] = 'import-excel/'
        return super().changelist_view(request, extra_context=extra_context)

admin.site.register(Book, BookAdmin)
