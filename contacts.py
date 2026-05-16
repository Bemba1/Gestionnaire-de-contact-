""""
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
import sqlite3
import csv
from tkinter import StringVar, END, PhotoImage
from tkinter import filedialog

import urllib.request
import json
import ssl

class Contacts:
    db_filename = 'contacts.db'
    RELATIONS = ["Prospect", "Client", "Collègue", "Prestataire", "Manager"]

    def __init__(self, root):
        

        self.supabase_url = "https://mnrowmfzdsahzeindnve.supabase.co/rest/v1/contacts_list"
        self.supabase_headers = {
            "apikey": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1ucm93bWZ6ZHNhaHplaW5kbnZlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzcxOTc0NDIsImV4cCI6MjA5Mjc3MzQ0Mn0.v7tG1tvzBtU_fBIItxPM0bNB4GrE15hb7A877SxBdt8",
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1ucm93bWZ6ZHNhaHplaW5kbnZlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzcxOTc0NDIsImV4cCI6MjA5Mjc3MzQ0Mn0.v7tG1tvzBtU_fBIItxPM0bNB4GrE15hb7A877SxBdt8",
            "Content-Type": "application/json"
        }
        self.ssl_context = ssl._create_unverified_context()


        




        self.root = root
        self.root.title("Gestionnaire de Contacts Moderne")
        self.root.resizable(True, True)
        self.style = ttk.Style()
        self.style.theme_use('darkly')

        self.ensure_database_schema()
        self.create_widgets()
        self.view_contacts()

    def ensure_database_schema(self):
        with sqlite3.connect(self.db_filename) as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(contacts_list)")
            columns = [col[1] for col in cursor.fetchall()]
            if 'relation' not in columns:
                cursor.execute("ALTER TABLE contacts_list ADD COLUMN relation TEXT DEFAULT 'Prospect'")
                conn.commit()
                print("Colonne 'relation' ajoutée à la table contacts_list")

    def execute_db_query(self, query, parameters=()):
        with sqlite3.connect(self.db_filename) as conn:
            cursor = conn.cursor()
            result = cursor.execute(query, parameters)
            conn.commit()
            return result

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill='both', expand=True)

        # Logo
        try:
            photo = PhotoImage(file='logo.png')
            logo_label = ttk.Label(main_frame, image=photo)
            logo_label.image = photo
            logo_label.grid(row=0, column=0, rowspan=2, padx=10, pady=10, sticky='nw')
        except:
            pass

        ttk.Label(
            main_frame,
            text="Gestionnaire de Contacts",
            font="-size 20 -weight bold",
            bootstyle=INFO
        ).grid(row=0, column=1, columnspan=2, pady=(10, 5), sticky='w')

        # Section Ajouter
        add_section = ttk.Frame(main_frame, padding=10, bootstyle=PRIMARY)
        add_section.grid(row=1, column=1, columnspan=2, padx=10, pady=10, sticky='ew')

        ttk.Label(
            add_section,
            text="Ajouter un contact",
            font="-size 12 -weight bold",
            bootstyle=PRIMARY
        ).pack(anchor='w', pady=(0, 10))

        add_inner = ttk.Frame(add_section, padding=10)
        add_inner.pack(fill='both', expand=True)

        ttk.Label(add_inner, text="Nom :", width=12).grid(row=0, column=0, padx=5, pady=8, sticky='e')
        self.namefield = ttk.Entry(add_inner, width=35, bootstyle=INFO)
        self.namefield.grid(row=0, column=1, padx=5, pady=8, sticky='w')

        ttk.Label(add_inner, text="Email :", width=12).grid(row=1, column=0, padx=5, pady=8, sticky='e')
        self.emailfield = ttk.Entry(add_inner, width=35, bootstyle=SUCCESS)
        self.emailfield.grid(row=1, column=1, padx=5, pady=8, sticky='w')

        ttk.Label(add_inner, text="Téléphone :", width=12).grid(row=2, column=0, padx=5, pady=8, sticky='e')
        self.numfield = ttk.Entry(add_inner, width=35, bootstyle=WARNING)
        self.numfield.grid(row=2, column=1, padx=5, pady=8, sticky='w')

        ttk.Label(add_inner, text="Relation :", width=12).grid(row=3, column=0, padx=5, pady=8, sticky='e')
        self.relation_var = StringVar(value=self.RELATIONS[0])
        self.relation_combo = ttk.Combobox(
            add_inner,
            textvariable=self.relation_var,
            values=self.RELATIONS,
            state="readonly",
            width=32,
            bootstyle=INFO
        )
        self.relation_combo.grid(row=3, column=1, padx=5, pady=8, sticky='w')

        ttk.Button(
            add_inner,
            text="Ajouter le contact",
            command=self.on_add_contact_button_clicked,
            bootstyle=(SUCCESS, OUTLINE),
            width=20
        ).grid(row=4, column=1, pady=15, sticky='e')

        # Zone recherche
        search_frame = ttk.Frame(main_frame, padding=10)
        search_frame.grid(row=2, column=1, columnspan=2, pady=5, sticky='ew')

        ttk.Label(search_frame, text="Rechercher :", width=12).pack(side='left', padx=(0, 8))
        self.search_var = StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=40, bootstyle=INFO)
        self.search_entry.pack(side='left', fill='x', expand=True, padx=5)

        ttk.Button(
            search_frame,
            text="Rechercher",
            command=self.on_search,
            bootstyle=(PRIMARY, OUTLINE),
            width=12
        ).pack(side='left', padx=5)

        self.search_var.trace('w', lambda *args: self.on_search())
        self.search_entry.bind('<Return>', lambda event: self.on_search())

        self.message = ttk.Label(main_frame, text="", bootstyle=DANGER, font="-size 10")
        self.message.grid(row=3, column=1, columnspan=2, pady=5, sticky='w')

        # Tableau
        tree_frame = ttk.Frame(main_frame)
        tree_frame.grid(row=4, column=0, columnspan=3, padx=10, pady=10, sticky='nsew')

        self.tree = ttk.Treeview(
            tree_frame,
            columns=("email", "number", "relation"),
            show='headings',
            height=12,
            bootstyle=PRIMARY
        )
        self.tree.heading("email", text="Email")
        self.tree.heading("number", text="Téléphone")
        self.tree.heading("relation", text="Relation")
        self.tree.column("email", width=220, anchor='w')
        self.tree.column("number", width=140, anchor='w')
        self.tree.column("relation", width=140, anchor='center')

        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree.yview, bootstyle=ROUND)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Boutons
        btn_frame = ttk.Frame(main_frame, padding=10)
        btn_frame.grid(row=5, column=0, columnspan=3, pady=15, sticky='ew')

        ttk.Button(
            btn_frame,
            text="Supprimer sélection",
            command=self.on_delete_selected_button_clicked,
            bootstyle=(DANGER, OUTLINE),
            width=18
        ).pack(side='left', padx=8)

        ttk.Button(
            btn_frame,
            text="Modifier sélection",
            command=self.on_modify_selected_button_clicked,
            bootstyle=(WARNING, OUTLINE),
            width=18
        ).pack(side='left', padx=8)

        ttk.Button(
            btn_frame,
            text="Exporter CSV",
            command=self.export_to_csv,
            bootstyle=(INFO, OUTLINE),
            width=15
        ).pack(side='right', padx=8)

        ttk.Button(
            btn_frame,
            text="Importer CSV",
            command=self.import_from_csv,
            bootstyle=(SUCCESS, OUTLINE),
            width=15
        ).pack(side='right', padx=8)

        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

    def on_add_contact_button_clicked(self):
        self.add_new_contact()

    def add_new_contact(self):
        name = self.namefield.get().strip()
        email = self.emailfield.get().strip()
        number = self.numfield.get().strip()
        relation = self.relation_var.get().strip()

        if not name or not email or not number:
            self.message.configure(text="Nom, email et téléphone obligatoires !", bootstyle=DANGER)
            return

        query = 'INSERT INTO contacts_list (name, email, number, relation) VALUES (?, ?, ?, ?)'
        self.execute_db_query(query, (name, email, number, relation))

        self.message.configure(text=f"Contact {name} ajouté ({relation})", bootstyle=SUCCESS)
        self.clear_fields()
        self.view_contacts()

    def clear_fields(self):
        self.namefield.delete(0, END)
        self.emailfield.delete(0, END)
        self.numfield.delete(0, END)
        self.relation_var.set(self.RELATIONS[0])

    def on_search(self):
        search_term = self.search_var.get().strip().lower()
        for item in self.tree.get_children():
            self.tree.delete(item)

        if not search_term:
            self.view_contacts()
            self.message.configure(text="", bootstyle=DEFAULT)
            return

        query = '''
            SELECT name, email, number, relation
            FROM contacts_list
            WHERE LOWER(name) LIKE ? OR LOWER(email) LIKE ? OR LOWER(number) LIKE ? OR LOWER(relation) LIKE ?
            ORDER BY name ASC
        '''
        pattern = f'%{search_term}%'
        parameters = (pattern, pattern, pattern, pattern)

        results = self.execute_db_query(query, parameters)
        count = 0
        for row in results:
            self.tree.insert('', END, values=(row[1], row[2], row[3]), text=row[0])
            count += 1

        if count == 0:
            self.message.configure(text="Aucun contact trouvé", bootstyle=WARNING)
        else:
            self.message.configure(text=f"{count} contact(s) trouvé(s)", bootstyle=SUCCESS)

    def view_contacts(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        req = urllib.request.Request(self.supabase_url, headers=self.supabase_headers)

    with urllib.request.urlopen(req, context=self.ssl_context) as response:
        data = json.loads(response.read().decode())

    for row in data:
        self.tree.insert(
            '',
            END,
            values=(row["email"], row["number"], row["relation"]),
            text=row["name"]
        )

    def on_delete_selected_button_clicked(self):
        selected = self.tree.selection()
        if not selected:
            self.message.configure(text="Aucun contact sélectionné", bootstyle=WARNING)
            return

        name = self.tree.item(selected)['text']
        if Messagebox.yesno(f"Supprimer le contact {name} ?", "Confirmation"):
            query = 'DELETE FROM contacts_list WHERE name = ?'
            self.execute_db_query(query, (name,))
            self.message.configure(text=f"Contact {name} supprimé", bootstyle=SUCCESS)
            self.view_contacts()

    def on_modify_selected_button_clicked(self):
        selected = self.tree.selection()
        if not selected:
            self.message.configure(text="Aucun contact sélectionné", bootstyle=WARNING)
            return

        # selected est un tuple → on prend le premier élément
        selected_item = selected[0]
        item_data = self.tree.item(selected_item)

        name = item_data['text']  # Le nom est dans 'text'
        values = item_data['values']

        email = values[0] if len(values) > 0 else ""
        number = values[1] if len(values) > 1 else ""
        relation = values[2] if len(values) > 2 else "Prospect"

        # Fenêtre de modification
        mod_win = ttk.Toplevel(self.root)
        mod_win.title(f"Modifier {name}")
        mod_win.geometry("520x480")
        mod_win.resizable(False, False)
        mod_win.grab_set()

        # On utilise un frame avec grid (pas de pack mélangé)
        frame = ttk.Frame(mod_win, padding=30)
        frame.pack(fill='both', expand=True)

        # Titre
        ttk.Label(
            frame,
            text="Modifier le contact",
            font="-size 16 -weight bold",
            bootstyle=INFO
        ).grid(row=0, column=0, columnspan=2, pady=(0, 25), sticky='w')

        # Champs avec grid uniquement
        ttk.Label(frame, text="Nom :", width=14).grid(row=1, column=0, padx=10, pady=12, sticky='e')
        name_var = StringVar(value=name)
        name_entry = ttk.Entry(frame, textvariable=name_var, width=40, bootstyle=INFO)
        name_entry.grid(row=1, column=1, padx=10, pady=12, sticky='w')

        ttk.Label(frame, text="Email :", width=14).grid(row=2, column=0, padx=10, pady=12, sticky='e')
        email_var = StringVar(value=email)
        email_entry = ttk.Entry(frame, textvariable=email_var, width=40, bootstyle=SUCCESS)
        email_entry.grid(row=2, column=1, padx=10, pady=12, sticky='w')

        ttk.Label(frame, text="Téléphone :", width=14).grid(row=3, column=0, padx=10, pady=12, sticky='e')
        number_var = StringVar(value=number)
        number_entry = ttk.Entry(frame, textvariable=number_var, width=40, bootstyle=WARNING)
        number_entry.grid(row=3, column=1, padx=10, pady=12, sticky='w')

        ttk.Label(frame, text="Relation :", width=14).grid(row=4, column=0, padx=10, pady=12, sticky='e')
        relation_var = StringVar(value=relation)
        relation_combo = ttk.Combobox(
            frame,
            textvariable=relation_var,
            values=self.RELATIONS,
            state="readonly",
            width=37,
            bootstyle=INFO
        )
        relation_combo.grid(row=4, column=1, padx=10, pady=12, sticky='w')

        def save_update():
            new_name = name_var.get().strip()
            new_email = email_var.get().strip()
            new_number = number_var.get().strip()
            new_relation = relation_var.get().strip()

            if not new_name or not new_email or not new_number:
                Messagebox.show_error("Nom, email et téléphone sont obligatoires", "Erreur")
                return

            query = '''
                UPDATE contacts_list
                SET name = ?, email = ?, number = ?, relation = ?
                WHERE name = ? AND number = ?
            '''
            parameters = (new_name, new_email, new_number, new_relation, name, number)

            try:
                self.execute_db_query(query, parameters)
                self.message.configure(text=f"Contact {new_name} mis à jour avec succès", bootstyle=SUCCESS)
                self.view_contacts()
                mod_win.destroy()
            except Exception as e:
                Messagebox.show_error(f"Erreur lors de la mise à jour : {str(e)}", "Erreur")

        ttk.Button(
            frame,
            text="Enregistrer les modifications",
            command=save_update,
            bootstyle=SUCCESS,
            width=25
        ).grid(row=5, column=1, pady=35, sticky='e')

        # On configure les colonnes pour centrer/étirer
        frame.columnconfigure(1, weight=1)

    def export_to_csv(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("Fichiers CSV", "*.csv")],
            title="Exporter les contacts en CSV"
        )
        if not file_path:
            return

        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Nom", "Email", "Téléphone", "Relation"])
                query = 'SELECT name, email, number, relation FROM contacts_list ORDER BY name ASC'
                contacts = self.execute_db_query(query)
                for row in contacts:
                    writer.writerow(row)
            self.message.configure(text=f"Export réussi : {file_path}", bootstyle=SUCCESS)
        except Exception as e:
            self.message.configure(text=f"Erreur lors de l'export : {str(e)}", bootstyle=DANGER)

    def import_from_csv(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Fichiers CSV", "*.csv")],
            title="Importer des contacts depuis CSV"
        )
        if not file_path:
            return

        added = 0
        skipped = 0

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader, None)  # saute l'en-tête

                for row in reader:
                    if len(row) < 3:
                        skipped += 1
                        continue

                    name = row[0].strip()
                    email = row[1].strip()
                    number = row[2].strip()
                    relation = row[3].strip() if len(row) > 3 else "Prospect"

                    if not name or not email or not number:
                        skipped += 1
                        continue

                    check_query = 'SELECT COUNT(*) FROM contacts_list WHERE name = ?'
                    exists = self.execute_db_query(check_query, (name,)).fetchone()[0]
                    if exists > 0:
                        skipped += 1
                        continue

                    query = 'INSERT INTO contacts_list (name, email, number, relation) VALUES (?, ?, ?, ?)'
                    self.execute_db_query(query, (name, email, number, relation))
                    added += 1

            self.message.configure(text=f"Import terminé : {added} ajoutés, {skipped} ignorés", bootstyle=SUCCESS)
            self.view_contacts()
        except Exception as e:
            self.message.configure(text=f"Erreur lors de l'import : {str(e)}", bootstyle=DANGER)

if __name__ == '__main__':
    root = ttk.Window(themename="darkly")
    root.attributes('-zoomed', True)
    app = Contacts(root)
    root.mainloop()

    
"""
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
import sqlite3
import csv
from tkinter import StringVar, END, PhotoImage
from tkinter import filedialog

import urllib.request
import json
import ssl


class Contacts:
    db_filename = 'contacts.db'
    RELATIONS = ["Prospect", "Client", "Collègue", "Prestataire", "Manager"]

    def __init__(self, root):

        # ✅ CONFIG SUPABASE
        self.supabase_url = "https://mnrowmfzdsahzeindnve.supabase.co/rest/v1/contacts_list"
        self.supabase_headers = {
            "apikey": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1ucm93bWZ6ZHNhaHplaW5kbnZlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzcxOTc0NDIsImV4cCI6MjA5Mjc3MzQ0Mn0.v7tG1tvzBtU_fBIItxPM0bNB4GrE15hb7A877SxBdt8",
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1ucm93bWZ6ZHNhaHplaW5kbnZlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzcxOTc0NDIsImV4cCI6MjA5Mjc3MzQ0Mn0.v7tG1tvzBtU_fBIItxPM0bNB4GrE15hb7A877SxBdt8",
            "Content-Type": "application/json"
        }
        self.ssl_context = ssl._create_unverified_context()

        self.root = root
        self.root.title("Gestionnaire de Contacts Moderne")
        self.root.resizable(True, True)
        self.style = ttk.Style()
        self.style.theme_use('darkly')

        self.create_widgets()
        self.view_contacts()

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill='both', expand=True)

        ttk.Label(
            main_frame,
            text="Gestionnaire de Contacts",
            font="-size 20 -weight bold",
            bootstyle=INFO
        ).pack(pady=10)

        self.tree = ttk.Treeview(
            main_frame,
            columns=("email", "number", "relation"),
            show='headings',
            height=12
        )

        self.tree.heading("email", text="Email")
        self.tree.heading("number", text="Téléphone")
        self.tree.heading("relation", text="Relation")

        self.tree.pack(fill='both', expand=True)

    # ✅ ICI LA BONNE VERSION (Supabase)
    def view_contacts(self):
        # vider tableau
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            # requête HTTP
            req = urllib.request.Request(
                self.supabase_url,
                headers=self.supabase_headers
            )

            # appel API
            with urllib.request.urlopen(req, context=self.ssl_context) as response:
                raw = response.read().decode()
                data = json.loads(raw)

            # affichage
            for row in data:
                self.tree.insert(
                    '',
                    END,
                    values=(
                        row["email"],
                        row["number"],
                        row["relation"]
                    ),
                    text=row["name"]
                )

        except Exception as e:
            print("Erreur Supabase :", e)


if __name__ == '__main__':
    root = ttk.Window(themename="darkly")
    root.attributes('-zoomed', True)
    app = Contacts(root)
    root.mainloop()
    