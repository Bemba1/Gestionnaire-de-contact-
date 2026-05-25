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

        # =========================
# FORMULAIRE AJOUT CONTACT
# =========================

form_frame = ttk.Frame(main_frame)
form_frame.pack(pady=15)

# NOM
ttk.Label(form_frame, text="Nom").grid(row=0, column=0, padx=5)
self.namefield = ttk.Entry(form_frame, width=20)
self.namefield.grid(row=0, column=1, padx=5)

# EMAIL
ttk.Label(form_frame, text="Email").grid(row=0, column=2, padx=5)
self.emailfield = ttk.Entry(form_frame, width=25)
self.emailfield.grid(row=0, column=3, padx=5)

# TELEPHONE
ttk.Label(form_frame, text="Téléphone").grid(row=0, column=4, padx=5)
self.numfield = ttk.Entry(form_frame, width=20)
self.numfield.grid(row=0, column=5, padx=5)

# RELATION
ttk.Label(form_frame, text="Relation").grid(row=0, column=6, padx=5)

self.relation_var = StringVar(value=self.RELATIONS[0])

self.relation_combo = ttk.Combobox(
    form_frame,
    textvariable=self.relation_var,
    values=self.RELATIONS,
    state="readonly",
    width=15
)

self.relation_combo.grid(row=0, column=7, padx=5)

# =========================
# BOUTONS
# =========================

button_frame = ttk.Frame(main_frame)
button_frame.pack(pady=10)

ttk.Button(
    button_frame,
    text="Ajouter Contact",
    command=self.add_new_contact,
    bootstyle=SUCCESS
).pack(side='left', padx=10)

ttk.Button(
    button_frame,
    text="Supprimer Contact",
    command=self.on_delete_selected_button_clicked,
    bootstyle=DANGER
).pack(side='left', padx=10)

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


        # =========================
# AJOUT CONTACT SUPABASE
# =========================

    def add_new_contact(self):

        name = self.namefield.get().strip()
        email = self.emailfield.get().strip()
        number = self.numfield.get().strip()
        relation = self.relation_var.get().strip()

        if not name or not email or not number:
            print("Champs obligatoires")
            return

        contact_data = {
            "name": name,
            "email": email,
            "number": number,
            "relation": relation
        }

        json_data = json.dumps(contact_data).encode("utf-8")

        req = urllib.request.Request(
            self.supabase_url,
            data=json_data,
            headers=self.supabase_headers,
            method="POST"
        )

        try:
            with urllib.request.urlopen(req, context=self.ssl_context) as response:
                print(response.read().decode())

            self.view_contacts()

        except Exception as e:
            print("Erreur ajout :", e)

# =========================
# SUPPRESSION CONTACT
# =========================

    def on_delete_selected_button_clicked(self):

        selected = self.tree.selection()

        if not selected:
            print("Aucun contact sélectionné")
            return

        selected_item = selected[0]

        item_data = self.tree.item(selected_item)

        email = item_data['values'][0]

        delete_url = self.supabase_url + "?email=eq." + email

        req = urllib.request.Request(
            delete_url,
            headers=self.supabase_headers,
            method="DELETE"
        )

        try:
            with urllib.request.urlopen(req, context=self.ssl_context) as response:
                print(response.read().decode())

            self.view_contacts()

        except Exception as e:
            print("Erreur suppression :", e)

if __name__ == '__main__':
    root = ttk.Window(themename="darkly")
    root.attributes('-zoomed', True)
    app = Contacts(root)
    root.mainloop()
    """


import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import urllib.request
import json
import ssl

from tkinter import StringVar, END


class Contacts:

    RELATIONS = [
        "Prospect",
        "Client",
        "Collègue",
        "Prestataire",
        "Manager"
    ]

    def __init__(self, root):

        # =========================
        # CONFIG SUPABASE
        # =========================

        self.supabase_url = "https://mnrowmfzdsahzeindnve.supabase.co/rest/v1/contacts_list"

        self.supabase_headers = {
            "apikey": "sb_publishable_VFOrqFncuWjQANlXNXtCWA_Gh5tb4FC",
            "Authorization": "Bearer sb_publishable_VFOrqFncuWjQANlXNXtCWA_Gh5tb4FC",
            "Content-Type": "application/json"
        }

        self.ssl_context = ssl._create_unverified_context()

        # =========================
        # FENETRE
        # =========================

        self.root = root
        self.root.title("Gestionnaire de Contacts Moderne")

        self.style = ttk.Style()
        self.style.theme_use("darkly")

        # création interface
        self.create_widgets()

        # chargement contacts
        self.view_contacts()

    # =========================
    # INTERFACE
    # =========================

    def create_widgets(self):

        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill='both', expand=True)

        ttk.Label(
            main_frame,
            text="Gestionnaire de Contacts",
            font="-size 20 -weight bold",
            bootstyle=INFO
        ).pack(pady=15)

        # =========================
        # TABLEAU
        # =========================

        self.tree = ttk.Treeview(
            main_frame,
            columns=("email", "number", "relation"),
            show='headings',
            height=15
        )

        self.tree.heading("email", text="Email")
        self.tree.heading("number", text="Téléphone")
        self.tree.heading("relation", text="Relation")

        self.tree.column("email", width=300)
        self.tree.column("number", width=200)
        self.tree.column("relation", width=150)

        self.tree.pack(fill='both', expand=True, pady=10)

        # =========================
        # FORMULAIRE
        # =========================

        form_frame = ttk.Frame(main_frame)
        form_frame.pack(pady=15)

        # NOM
        ttk.Label(form_frame, text="Nom").grid(
            row=0,
            column=0,
            padx=5
        )

        self.namefield = ttk.Entry(form_frame, width=20)

        self.namefield.grid(
            row=0,
            column=1,
            padx=5
        )

        # EMAIL
        ttk.Label(form_frame, text="Email").grid(
            row=0,
            column=2,
            padx=5
        )

        self.emailfield = ttk.Entry(form_frame, width=25)

        self.emailfield.grid(
            row=0,
            column=3,
            padx=5
        )

        # TELEPHONE
        ttk.Label(form_frame, text="Téléphone").grid(
            row=0,
            column=4,
            padx=5
        )

        self.numfield = ttk.Entry(form_frame, width=20)

        self.numfield.grid(
            row=0,
            column=5,
            padx=5
        )

        # RELATION
        ttk.Label(form_frame, text="Relation").grid(
            row=0,
            column=6,
            padx=5
        )

        self.relation_var = StringVar(
            value=self.RELATIONS[0]
        )

        self.relation_combo = ttk.Combobox(
            form_frame,
            textvariable=self.relation_var,
            values=self.RELATIONS,
            state="readonly",
            width=15
        )

        self.relation_combo.grid(
            row=0,
            column=7,
            padx=5
        )

        # =========================
        # BOUTONS
        # =========================

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=15)

        ttk.Button(
            button_frame,
            text="Ajouter Contact",
            command=self.add_new_contact,
            bootstyle=SUCCESS
        ).pack(
            side='left',
            padx=10
        )

        ttk.Button(
            button_frame,
            text="Supprimer Contact",
            command=self.on_delete_selected_button_clicked,
            bootstyle=DANGER
        ).pack(
            side='left',
            padx=10
        )

    # =========================
    # AFFICHER CONTACTS
    # =========================

    def view_contacts(self):

        # vider tableau
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:

            req = urllib.request.Request(
                self.supabase_url,
                headers=self.supabase_headers
            )

            with urllib.request.urlopen(
                req,
                context=self.ssl_context
            ) as response:

                raw = response.read().decode()

                data = json.loads(raw)

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

    # =========================
    # AJOUT CONTACT
    # =========================

    def add_new_contact(self):

        name = self.namefield.get().strip()
        email = self.emailfield.get().strip()
        number = self.numfield.get().strip()
        relation = self.relation_var.get().strip()

        if not name or not email or not number:
            print("Tous les champs sont obligatoires")
            return

        contact_data = {
            "name": name,
            "email": email,
            "number": number,
            "relation": relation
        }

        json_data = json.dumps(contact_data).encode("utf-8")

        req = urllib.request.Request(
            self.supabase_url,
            data=json_data,
            headers=self.supabase_headers,
            method="POST"
        )

        try:

            with urllib.request.urlopen(
                req,
                context=self.ssl_context
            ) as response:

                print(response.read().decode())

            # refresh tableau
            self.view_contacts()

            # vider champs
            self.namefield.delete(0, END)
            self.emailfield.delete(0, END)
            self.numfield.delete(0, END)

        except Exception as e:
            print("Erreur ajout :", e)

    # =========================
    # SUPPRESSION CONTACT
    # =========================

    def on_delete_selected_button_clicked(self):

        selected = self.tree.selection()

        if not selected:
            print("Aucun contact sélectionné")
            return

        selected_item = selected[0]

        item_data = self.tree.item(selected_item)

        email = item_data['values'][0]

        delete_url = self.supabase_url + "?email=eq." + email

        req = urllib.request.Request(
            delete_url,
            headers=self.supabase_headers,
            method="DELETE"
        )

        try:

            with urllib.request.urlopen(
                req,
                context=self.ssl_context
            ) as response:

                print(response.read().decode())

            # refresh tableau
            self.view_contacts()

        except Exception as e:
            print("Erreur suppression :", e)


# =========================
# LANCEMENT APP
# =========================

if __name__ == '__main__':

    root = ttk.Window(themename="darkly")

    root.attributes('-zoomed', True)

    app = Contacts(root)

    root.mainloop()