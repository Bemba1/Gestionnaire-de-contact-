import ttkbootstrap as ttk 
from ttkbootstrap.constants import *
from ttkbootstrap.widgets.tableview import Tableview
import mysql.connector
from dotenv import load_dotenv
import os
from tkinter import simpledialog, messagebox

# Charger les variables d'environnement
load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

# Connexion BDD
def get_db_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

def charger_contacts():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, prenom, nom, telephone, email FROM contacts ORDER BY id ASC")
        rows = cursor.fetchall()
        conn.close()
        data = [[row["id"], row["prenom"], row["nom"], row["telephone"], row["email"]] for row in rows]
        return data
    except Exception as e:
        print("Erreur BDD:", e)
        return []

def filtrer_contacts_db(query):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        sql = """
            SELECT id, prenom, nom, telephone, email
            FROM contacts
            WHERE prenom LIKE %s OR nom LIKE %s
            ORDER BY id ASC
        """
        param = (f"%{query}%", f"%{query}%")
        cursor.execute(sql, param)
        rows = cursor.fetchall()
        conn.close()
        data = [[row["id"], row["prenom"], row["nom"], row["telephone"], row["email"]] for row in rows]
        return data
    except Exception as e:
        print("Erreur BDD:", e)
        return []

# Fenêtre principale
app = ttk.Window(title="Gestionnaire de Contacts", themename="superhero")
app.geometry("1000x700")

# Titre
ttk.Label(app, text="Mes Contacts", font=("Helvetica", 28, "bold"), bootstyle="primary").pack(pady=20)

# Barre de recherche avec bouton
search_frame = ttk.Frame(app)
search_frame.pack(fill=X, padx=50, pady=10)
ttk.Label(search_frame, text="Rechercher :", font=("Helvetica", 12)).pack(side=LEFT)
search_var = ttk.StringVar()
search_entry = ttk.Entry(search_frame, textvariable=search_var, font=("Helvetica", 12), width=40)
search_entry.pack(side=LEFT, padx=10)

def on_rechercher():
    query = search_var.get().strip()
    if query == "":
        data = charger_contacts()
    else:
        data = filtrer_contacts_db(query)
    table.build_table_data(coldata=cols, rowdata=data)

ttk.Button(search_frame, text="Rechercher", bootstyle="info", command=on_rechercher).pack(side=LEFT, padx=10)

# Table
cols = [
    {"text": "ID", "stretch": False},
    {"text": "Prénom", "stretch": True},
    {"text": "Nom", "stretch": True},
    {"text": "Téléphone", "stretch": True},
    {"text": "Email", "stretch": True},
]

table = Tableview(
    master=app,
    coldata=cols,
    rowdata=charger_contacts(),
    paginated=True,
    pagesize=15,
    searchable=False,
    bootstyle="primary",
    stripecolor=("#2b2b2b", "#1e1e1e"),
)
table.pack(fill=BOTH, expand=True, padx=50, pady=20)

# Fonctions CRUD
def ajouter_contact():
    prenom = simpledialog.askstring("Ajouter", "Prénom :")
    if not prenom: return
    nom = simpledialog.askstring("Ajouter", "Nom :")
    telephone = simpledialog.askstring("Ajouter", "Téléphone :")
    email = simpledialog.askstring("Ajouter", "Email :")
    if not nom or not telephone or not email:
        messagebox.showwarning("Attention", "Tous les champs doivent être remplis")
        return
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO contacts (id_user_supabase, prenom, nom, telephone, email) "
            "VALUES ('11111111-1111-1111-1111-111111111111', %s, %s, %s, %s)",
            (prenom, nom, telephone, email)
        )
        conn.commit()
        conn.close()
        table.build_table_data(coldata=cols, rowdata=charger_contacts())
    except Exception as e:
        messagebox.showerror("Erreur", f"Impossible d'ajouter le contact : {e}")

def modifier_contact():
    selected = table.get_row()
    if not selected:
        messagebox.showwarning("Alerte", "Veuillez sélectionner un contact")
        return
    contact_id = selected[0]
    prenom = simpledialog.askstring("Modifier", "Prénom :", initialvalue=selected[1])
    nom = simpledialog.askstring("Modifier", "Nom :", initialvalue=selected[2])
    telephone = simpledialog.askstring("Modifier", "Téléphone :", initialvalue=selected[3])
    email = simpledialog.askstring("Modifier", "Email :", initialvalue=selected[4])
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE contacts SET prenom=%s, nom=%s, telephone=%s, email=%s WHERE id=%s",
            (prenom, nom, telephone, email, contact_id)
        )
        conn.commit()
        conn.close()
        table.build_table_data(coldata=cols, rowdata=charger_contacts())
    except Exception as e:
        messagebox.showerror("Erreur", f"Impossible de modifier le contact : {e}")

def supprimer_contact():
    selected = table.get_row()
    if not selected:
        messagebox.showwarning("Alerte", "Veuillez sélectionner un contact")
        return
    contact_id = selected[0]
    if not messagebox.askyesno("Confirmer", "Voulez-vous vraiment supprimer ce contact ?"):
        return
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM contacts WHERE id=%s", (contact_id,))
        conn.commit()
        conn.close()
        table.build_table_data(coldata=cols, rowdata=charger_contacts())
    except Exception as e:
        messagebox.showerror("Erreur", f"Impossible de supprimer le contact : {e}")

# Boutons CRUD
btn_frame = ttk.Frame(app)
btn_frame.pack(pady=20)
ttk.Button(btn_frame, text="Ajouter un contact", bootstyle="success-outline", width=20, command=ajouter_contact).pack(side=LEFT, padx=10)
ttk.Button(btn_frame, text="Modifier", bootstyle="warning-outline", width=15, command=modifier_contact).pack(side=LEFT, padx=10)
ttk.Button(btn_frame, text="Supprimer", bootstyle="danger-outline", width=15, command=supprimer_contact).pack(side=LEFT, padx=10)
ttk.Button(btn_frame, text="Actualiser", bootstyle="info", width=15, command=lambda: table.build_table_data(coldata=cols, rowdata=charger_contacts())).pack(side=LEFT, padx=10)

# Lancer l'application
app.mainloop()
