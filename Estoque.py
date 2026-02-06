from datetime import datetime
import sqlite3
import threading
from flask import Flask, request, redirect, render_template_string, session
from tkinter import messagebox, simpledialog
import customtkinter as ctk

janela_estoque = None
janela_registro = None
janela_resumo = None
janela_produto = None
janela_uso = None
janela_principal = None
janela_reparo = None
janela_criar_usuario = None
janela_trocar_senha = None
janela_remover_usuario = None
janela_trocar_senha_master = None


#conn = sqlite3.connect("estoque.db")
#cur = conn.cursor()

#cur.execute("PRAGMA table_info(uso_material);")
#colunas = cur.fetchall()

#for c in colunas:
  #  print(c)

#conn.close()
# ================= CONFIG =================
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

usuario_logado = {"nome": "", "permissao": ""}

def trocar_senha():
    global janela_trocar_senha

    if janela_trocar_senha and janela_trocar_senha.winfo_exists():
        janela_trocar_senha.lift()
        janela_trocar_senha.focus_force()
        return

    janela_trocar_senha = ctk.CTkToplevel(janela_principal)
    win = janela_trocar_senha

    win.title("Trocar Senha")
    win.geometry("390x400")
    win.resizable(False, False)

    win.transient(janela_principal)
    win.lift()
    win.attributes("-topmost", True)
    win.after(300, lambda: win.attributes("-topmost", False))
    win.focus_force()

    frame = ctk.CTkFrame(win)
    frame.pack(expand=True, fill="both", padx=20, pady=20)

    ctk.CTkLabel(
        frame,
        text="Trocar Senha",
        font=("Arial", 18, "bold")
    ).pack(pady=15)

    # ===== SENHA ATUAL =====
    ctk.CTkLabel(frame, text="Senha atual").pack(anchor="w", padx=20)
    entrada_atual = ctk.CTkEntry(frame, show="*")
    entrada_atual.pack(fill="x", padx=20, pady=5)

    # ===== NOVA SENHA =====
    ctk.CTkLabel(frame, text="Nova senha").pack(anchor="w", padx=20)
    entrada_nova = ctk.CTkEntry(frame, show="*")
    entrada_nova.pack(fill="x", padx=20, pady=5)

    # ===== CONFIRMAR =====
    ctk.CTkLabel(frame, text="Confirmar nova senha").pack(anchor="w", padx=20)
    entrada_confirmar = ctk.CTkEntry(frame, show="*")
    entrada_confirmar.pack(fill="x", padx=20, pady=5)

    msg = ctk.CTkLabel(frame, text="", text_color="red")
    msg.pack(pady=10)

    def salvar():
        atual = entrada_atual.get()
        nova = entrada_nova.get()
        confirmar = entrada_confirmar.get()

        if not atual or not nova or not confirmar:
            msg.configure(text="Preencha todos os campos", text_color="red")
            return

        if nova != confirmar:
            msg.configure(text="As novas senhas não coincidem", text_color="red")
            return

        conn = conectar_db()
        c = conn.cursor()

        # 🔐 valida senha atual
        c.execute(
            "SELECT senha FROM usuarios WHERE usuario=?",
            (usuario_logado["nome"],)
        )
        senha_bd = c.fetchone()

        if not senha_bd or senha_bd[0] != atual:
            conn.close()
            msg.configure(text="Senha atual incorreta", text_color="red")
            return

        # 💾 atualiza senha
        c.execute(
            "UPDATE usuarios SET senha=? WHERE usuario=?",
            (nova, usuario_logado["nome"])
        )
        conn.commit()
        conn.close()

        msg.configure(
            text="Senha alterada com sucesso",
            text_color="green"
        )

        entrada_atual.delete(0, "end")
        entrada_nova.delete(0, "end")
        entrada_confirmar.delete(0, "end")

    ctk.CTkButton(
        frame,
        text="Salvar Nova Senha",
        height=42,
        fg_color="#1f6aa5",
        command=salvar
    ).pack(fill="x", padx=40, pady=15)

def master_trocar_senha_usuario():
    if usuario_logado["permissao"] != "master":
        messagebox.showerror("Permissão", "Apenas MASTER")
        return
    global janela_trocar_senha_master

    if janela_trocar_senha_master and janela_trocar_senha_master.winfo_exists():
        janela_trocar_senha_master.lift()
        janela_trocar_senha_master.focus_force()
        return

    janela_trocar_senha_master = ctk.CTkToplevel(janela_principal)
    win = janela_trocar_senha_master
    win.title("Trocar Senha Master")
    win.geometry("440x560")
    win.resizable(False, False)


    win.transient(janela_principal)
    win.lift()
    win.attributes("-topmost", True)
    win.after(300, lambda: win.attributes("-topmost", False))
    win.focus_force()

    frame = ctk.CTkFrame(win)
    frame.pack(expand=True, fill="both", padx=20, pady=20)

    # ===== TÍTULO =====
    ctk.CTkLabel(
        frame,
        text="Trocar Senha de Usuário",
        font=("Arial", 18, "bold")
    ).pack(pady=(10, 15))

    # ===== LISTA USUÁRIOS =====
    ctk.CTkLabel(
        frame,
        text="Usuários cadastrados",
        font=("Arial", 13, "bold")
    ).pack(anchor="w", padx=20)

    painel = ctk.CTkFrame(frame, height=180)
    painel.pack(fill="x", padx=20, pady=(5, 15))
    painel.pack_propagate(False)  # 🔒 trava altura

    usuario_sel = ctk.StringVar(value="")
    msg = ctk.CTkLabel(frame, text="", text_color="red")
    msg.pack(pady=5)

    def carregar_usuarios():
        for w in painel.winfo_children():
            w.destroy()

        conn = conectar_db()
        c = conn.cursor()
        c.execute("SELECT usuario, permissao FROM usuarios ORDER BY usuario")
        usuarios = c.fetchall()
        conn.close()

        for u, p in usuarios:
            btn = ctk.CTkButton(
                painel,
                text=f"{u} ({p})",
                height=34,
                anchor="w",
                fg_color="#2b2b2b",
                hover_color="#3a3a3a",
                command=lambda nome=u: selecionar_usuario(nome)
            )
            btn.pack(fill="x", padx=6, pady=4)

    def selecionar_usuario(nome):
        usuario_sel.set(nome)
        msg.configure(
            text=f"Usuário selecionado: {nome}",
            text_color="white"
        )

    carregar_usuarios()

    # ===== NOVA SENHA =====
    ctk.CTkLabel(frame, text="Nova senha", font=("Arial", 13, "bold"))\
        .pack(anchor="w", padx=20, pady=(10, 0))

    entrada_nova = ctk.CTkEntry(frame, show="*")
    entrada_nova.pack(fill="x", padx=20, pady=5)

    ctk.CTkLabel(frame, text="Confirmar nova senha", font=("Arial", 13, "bold"))\
        .pack(anchor="w", padx=20)

    entrada_confirmar = ctk.CTkEntry(frame, show="*")
    entrada_confirmar.pack(fill="x", padx=20, pady=5)

    # ===== SALVAR =====
    def salvar():
        usuario = usuario_sel.get()
        nova = entrada_nova.get()
        confirmar = entrada_confirmar.get()

        if not usuario or not nova or not confirmar:
            msg.configure(text="Preencha todos os campos", text_color="red")
            return

        if usuario == usuario_logado["nome"]:
            msg.configure(
                text="Use 'Trocar Senha' para sua própria conta",
                text_color="red"
            )
            return

        if nova != confirmar:
            msg.configure(text="As senhas não coincidem", text_color="red")
            return

        conn = conectar_db()
        c = conn.cursor()
        c.execute(
            "UPDATE usuarios SET senha=? WHERE usuario=?",
            (nova, usuario)
        )
        conn.commit()
        conn.close()

        msg.configure(
            text=f"Senha do usuário '{usuario}' alterada com sucesso",
            text_color="green"
        )

        entrada_nova.delete(0, "end")
        entrada_confirmar.delete(0, "end")
        usuario_sel.set("")

    ctk.CTkButton(
        frame,
        text="Salvar Nova Senha",
        height=44,
        fg_color="#1f6aa5",
        command=salvar
    ).pack(fill="x", padx=40, pady=(20, 10))

LIMITE_ESTOQUE_BAIXO = 1

# ================= BANCO =================
def conectar_db():
    return sqlite3.connect("estoque.db", check_same_thread=False)

def criar_tabelas():
    conn = conectar_db()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS maquinas (
            nome TEXT PRIMARY KEY
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS estoque (
            produto TEXT PRIMARY KEY,
            quantidade INTEGER
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            usuario TEXT PRIMARY KEY,
            senha TEXT,
            permissao TEXT
        )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS uso_material (
        data TEXT,
        maquina TEXT,
        numero_maquina TEXT,
        produto TEXT,
        quantidade INTEGER,
        usuario TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS reparos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data TEXT,
        maquina TEXT,
        numero_maquina TEXT,
        produto TEXT,
        quantidade INTEGER,
        usuario TEXT
    )
    """)

    # ==== CRIA USUÁRIO MASTER PADRÃO (SE NÃO EXISTIR) ====
    c.execute(
        "INSERT OR IGNORE INTO usuarios VALUES (?, ?, ?)",
        ("master", "master123", "master")
    )

    try:
        c.execute("ALTER TABLE uso_material ADD COLUMN numero_maquina TEXT")
    except:
        pass
    conn.commit()
    conn.close()

# ================= LOGIN =================
def autenticar():
    u = simpledialog.askstring("Login", "Usuário:")
    s = simpledialog.askstring("Login", "Senha:", show="*")

    conn = conectar_db()
    c = conn.cursor()
    c.execute("SELECT permissao FROM usuarios WHERE usuario=? AND senha=?", (u, s))
    r = c.fetchone()
    conn.close()

    if r:
        usuario_logado["nome"] = u
        usuario_logado["permissao"] = r[0]
        return True
    return False

def apenas_admin():
    if usuario_logado["permissao"] not in ("admin", "master"):
        messagebox.showerror("Permissão", "Apenas ADMIN ou MASTER")
        return False
    return True


def apenas_master():
    if usuario_logado["permissao"] != "master":
        messagebox.showerror("Permissão", "Apenas MASTER")
        return False
    return True

# ================= USUÁRIOS =================
def criar_usuario():
    global janela_criar_usuario

    if janela_criar_usuario and janela_criar_usuario.winfo_exists():
        janela_criar_usuario.lift()
        janela_criar_usuario.focus_force()
        return

    janela_criar_usuario = ctk.CTkToplevel(janela_principal)
    win = janela_criar_usuario

    win.title("Criar Usuário")
    win.geometry("390x350")
    win.resizable(False, False)

    win.transient(janela_principal)
    win.lift()
    win.attributes("-topmost", True)
    win.after(300, lambda: win.attributes("-topmost", False))
    win.focus_force()

    frame = ctk.CTkFrame(win)
    frame.pack(expand=True, fill="both", padx=20, pady=20)

    # ---- USUÁRIO ----
    ctk.CTkLabel(frame, text="usuario", font=("Arial", 14, "bold"))\
        .pack(pady=(10, 5))
    entrada_user = ctk.CTkEntry(frame)
    entrada_user.pack(fill="x", padx=40)

    # ---- SENHA ----
    ctk.CTkLabel(frame, text="senha", font=("Arial", 14, "bold"))\
        .pack(pady=(15, 5))
    entrada_senha = ctk.CTkEntry(frame, show="*")
    entrada_senha.pack(fill="x", padx=40)

    # ---- PERMISSÃO ----
    permissao = ctk.StringVar(value="")

    frame_perm = ctk.CTkFrame(frame)
    frame_perm.pack(pady=25)

    COR_PADRAO = "#1f6aa5"
    COR_SELECIONADO = "#144870"

    btn_admin = ctk.CTkButton(frame_perm, text="admin", width=140)
    btn_user = ctk.CTkButton(frame_perm, text="usuario", width=140)

    def selecionar_perm(p):
        permissao.set(p)

        btn_admin.configure(
            fg_color=COR_SELECIONADO if p == "admin" else COR_PADRAO
        )
        btn_user.configure(
            fg_color=COR_SELECIONADO if p == "usuario" else COR_PADRAO
        )

    btn_admin.configure(command=lambda: selecionar_perm("admin"))
    btn_user.configure(command=lambda: selecionar_perm("usuario"))

    btn_admin.grid(row=0, column=0, padx=10)
    btn_user.grid(row=0, column=1, padx=10)

    msg = ctk.CTkLabel(frame, text="", text_color="red")
    msg.pack(pady=10)

    # ---- SALVAR ----
    def salvar():
        u = entrada_user.get().strip()
        s = entrada_senha.get().strip()
        p = permissao.get()

        if not u or not s or not p:
            msg.configure(text="Preencha todos os campos", text_color="red")
            return

        # 🔐 SOMENTE MASTER CRIA ADMIN
        if p == "admin" and usuario_logado["permissao"] != "master":
            msg.configure(
                text="Somente o MASTER pode criar ADMIN",
                text_color="red"
            )
            return

        conn = conectar_db()
        c = conn.cursor()

        # 🚫 LIMITA A 1 ADMIN
        if p == "admin":
            c.execute(
                "SELECT COUNT(*) FROM usuarios WHERE permissao='admin'"
            )
            total_admin = c.fetchone()[0]

            if total_admin >= 1:
                conn.close()
                msg.configure(
                    text="Já existe um ADMIN cadastrado",
                    text_color="red"
                )
                return

        try:
            c.execute(
                "INSERT INTO usuarios VALUES (?,?,?)",
                (u, s, p)
            )
            conn.commit()
            msg.configure(text="Usuário criado com sucesso", text_color="green")
        except sqlite3.IntegrityError:
            msg.configure(text="Usuário já existe", text_color="red")

        conn.close()

        entrada_user.delete(0, "end")
        entrada_senha.delete(0, "end")
        permissao.set("")
        btn_admin.configure(fg_color=COR_PADRAO)
        btn_user.configure(fg_color=COR_PADRAO)

    ctk.CTkButton(
        frame,
        text="salvar",
        height=42,
        fg_color="#2b9348",
        command=salvar
    ).pack(fill="x", padx=60, pady=(10, 0))

def remover_usuario():
    global janela_remover_usuario

    if janela_remover_usuario and janela_remover_usuario.winfo_exists():
        janela_remover_usuario.lift()
        janela_remover_usuario.focus_force()
        return

    janela_remover_usuario = ctk.CTkToplevel(janela_principal)
    win = janela_remover_usuario
    win.title("Remover Usuário")
    win.geometry("440x560")
    win.resizable(False, False)

    win.transient(janela_principal)
    win.lift()
    win.attributes("-topmost", True)
    win.after(300, lambda: win.attributes("-topmost", False))
    win.focus_force()

    frame = ctk.CTkFrame(win)
    frame.pack(expand=True, fill="both", padx=20, pady=20)

    # ---- CAMPO USUÁRIO ----
    ctk.CTkLabel(frame, text="usuario", font=("Arial", 14, "bold"))\
        .pack(pady=(10, 5))

    entrada_user = ctk.CTkEntry(frame)
    entrada_user.pack(fill="x", padx=40)

    msg = ctk.CTkLabel(frame, text="", text_color="red")
    msg.pack(pady=6)

    # ENTER remove
    entrada_user.bind("<Return>", lambda e: remover())

    # ---- PAINEL DE USUÁRIOS ----
    ctk.CTkLabel(
        frame,
        text="usuarios cadastrados",
        font=("Arial", 13, "bold")
    ).pack(pady=(15, 5))

    painel = ctk.CTkScrollableFrame(frame, height=260)
    painel.pack(fill="x", padx=20)

    def carregar_usuarios():
        for w in painel.winfo_children():
            w.destroy()

        conn = conectar_db()
        c = conn.cursor()
        c.execute("SELECT usuario, permissao FROM usuarios ORDER BY usuario")
        usuarios = c.fetchall()
        conn.close()

        for u, p in usuarios:
            texto = f"{u} ({p})"
            btn = ctk.CTkButton(
                painel,
                text=texto,
                height=32,
                anchor="w",
                fg_color="#2b2b2b",
                hover_color="#3a3a3a",
                command=lambda nome=u: selecionar_usuario(nome)
            )
            btn.pack(fill="x", pady=2, padx=4)

    def selecionar_usuario(nome):
        entrada_user.delete(0, "end")
        entrada_user.insert(0, nome)
        entrada_user.focus()

    # ---- REMOVER ----
    def remover():
        u = entrada_user.get().strip()

        if not u:
            msg.configure(text="Informe o usuário", text_color="red")
            return

        if u == "master":
            msg.configure(text="MASTER não pode ser removido", text_color="red")
            return
        
        conn = conectar_db()
        c = conn.cursor()
        c.execute("SELECT permissao FROM usuarios WHERE usuario=?", (u,))
        res = c.fetchone()
        conn.close()

        if res and res[0] == "admin" and usuario_logado["permissao"] != "master":
            msg.configure(
                text="Somente o MASTER pode remover ADMIN",
                text_color="red"
            )
            return

        confirmar = messagebox.askyesno(
            "Confirmar exclusão",
            f"Deseja realmente remover o usuário '{u}'?"
        )
        if not confirmar:
            return

        conn = conectar_db()
        c = conn.cursor()
        c.execute("DELETE FROM usuarios WHERE usuario=?", (u,))
        conn.commit()
        conn.close()

        msg.configure(
            text="Usuário removido com sucesso",
            text_color="green"
        )
        entrada_user.delete(0, "end")
        carregar_usuarios()

    ctk.CTkButton(
        frame,
        text="remover",
        height=42,
        fg_color="#c1121f",
        command=remover
    ).pack(fill="x", padx=60, pady=15)

    carregar_usuarios()

# ================= ESTOQUE =================
def adicionar_produto():
    global janela_produto

    if janela_produto and janela_produto.winfo_exists():
        janela_produto.lift()
        janela_produto.focus_force()
        return

    janela_produto = ctk.CTkToplevel(janela_principal)
    win = janela_produto

    win.title("Cadastro de Produtos")
    win.geometry("440x600")
    win.resizable(False, False)

    # 🔥 GARANTE QUE FIQUE POR CIMA DO MENU
    win.lift()
    win.focus_force()
    win.attributes("-topmost", True)
    win.after(200, lambda: win.attributes("-topmost", False))

    win.protocol(
        "WM_DELETE_WINDOW",
        lambda: (win.destroy(), globals().__setitem__("janela_produto", None))
    )

    # ===== FRAME COM SCROLL =====
    scroll = ctk.CTkScrollableFrame(win)
    scroll.pack(expand=True, fill="both", padx=15, pady=15)

    ctk.CTkLabel(
        scroll, text="Cadastro de Produtos", font=("Arial", 18, "bold")
    ).pack(pady=10)

    # ================= PRODUTOS EXISTENTES =================
    ctk.CTkLabel(
        scroll, text="Produtos existentes", font=("Arial", 14, "bold")
    ).pack(anchor="w", padx=10)

    lista = ctk.CTkScrollableFrame(scroll, height=160)
    lista.pack(fill="x", padx=10, pady=5)

    conn = conectar_db()
    c = conn.cursor()
    c.execute("SELECT produto FROM estoque ORDER BY produto")
    produtos = [p[0] for p in c.fetchall()]
    conn.close()

    produto_sel = ctk.StringVar(value="")

    msg = ctk.CTkLabel(scroll, text="", text_color="red")
    msg.pack(pady=6)

    def selecionar(nome):
        produto_sel.set(nome)
        msg.configure(text=f"Selecionado: {nome}", text_color="white")

    for p in produtos:
        ctk.CTkButton(
            lista,
            text=p,
            anchor="w",
            height=32,
            command=lambda n=p: selecionar(n)
        ).pack(fill="x", pady=2)

    # ================= QUANTIDADE =================
    ctk.CTkLabel(
        scroll, text="Quantidade a adicionar"
    ).pack(anchor="w", padx=10, pady=(10, 0))

    entrada_qtd = ctk.CTkEntry(scroll, placeholder_text="Ex: 10")
    entrada_qtd.pack(fill="x", padx=10, pady=5)

    # ================= NOVO PRODUTO =================
    ctk.CTkLabel(
        scroll, text="Novo produto", font=("Arial", 14, "bold")
    ).pack(anchor="w", padx=10, pady=(15, 0))

    entrada_nome = ctk.CTkEntry(scroll, placeholder_text="Nome do produto")
    entrada_nome.pack(fill="x", padx=10, pady=5)

    entrada_qtd_novo = ctk.CTkEntry(scroll, placeholder_text="Quantidade inicial")
    entrada_qtd_novo.pack(fill="x", padx=10, pady=5)

    # ================= AÇÕES =================
    def adicionar_quantidade():
        produto = produto_sel.get()
        qtd = entrada_qtd.get()

        if not produto:
            msg.configure(text="Selecione um produto existente", text_color="red")
            return

        if not qtd.isdigit():
            msg.configure(text="Quantidade inválida", text_color="red")
            return

        conn = conectar_db()
        c = conn.cursor()
        c.execute(
            "UPDATE estoque SET quantidade = quantidade + ? WHERE produto = ?",
            (int(qtd), produto)
        )
        conn.commit()
        conn.close()

        msg.configure(text="Quantidade salva com sucesso", text_color="green")
        entrada_qtd.delete(0, "end")

    def criar_produto():
        nome = entrada_nome.get().strip().lower()
        qtd = entrada_qtd_novo.get()

        if not nome:
            msg.configure(text="Informe o nome do produto", text_color="red")
            return

        if not qtd.isdigit():
            msg.configure(text="Quantidade inválida", text_color="red")
            return

        conn = conectar_db()
        c = conn.cursor()
        c.execute(
            "INSERT OR IGNORE INTO estoque VALUES (?, ?)",
            (nome, int(qtd))
        )
        conn.commit()
        conn.close()

        msg.configure(text="Produto criado com sucesso", text_color="green")
        entrada_nome.delete(0, "end")
        entrada_qtd_novo.delete(0, "end")

    # ================= BOTÕES (AGORA VISÍVEIS) =================
    ctk.CTkButton(
        scroll,
        text="Salvar Quantidade do Produto Selecionado",
        height=42,
        command=adicionar_quantidade
    ).pack(fill="x", padx=10, pady=(10, 5))

    ctk.CTkButton(
        scroll,
        text="Salvar Novo Produto",
        height=42,
        fg_color="#1f6aa5",
        command=criar_produto
    ).pack(fill="x", padx=10, pady=(0, 15))

def listar_estoque():
    global janela_estoque

    if janela_estoque and janela_estoque.winfo_exists():
        janela_estoque.lift()
        janela_estoque.focus_force()
        return

    conn = conectar_db()
    c = conn.cursor()
    c.execute("SELECT produto, quantidade FROM estoque ORDER BY produto")
    dados = c.fetchall()
    conn.close()

    janela_estoque = ctk.CTkToplevel()
    win = janela_estoque
    win.title("Estoque Atual")
    win.geometry("450x420")

    win.lift()
    win.focus_force()
    win.attributes("-topmost", True)
    win.after(200, lambda: win.attributes("-topmost", False))
    #win.grab_set() # menu so se fechar a janela

    scroll = ctk.CTkScrollableFrame(win, width=420, height=380)
    scroll.pack(padx=10, pady=10, fill="both", expand=True)

    # Cabeçalhos
    headers = ["Produto", "Quantidade"]
    for col, h in enumerate(headers):
        ctk.CTkLabel(
            scroll,
            text=h,
            font=("Arial", 13, "bold"),
            width=220 if col == 0 else 120
        ).grid(row=0, column=col, padx=12, pady=8, sticky="w")

    # Dados
    for i, (p, q) in enumerate(dados, start=1):
        alerta = " ⚠️" if q <= LIMITE_ESTOQUE_BAIXO else ""

        ctk.CTkLabel(
            scroll,
            text=p,
            width=220
        ).grid(row=i, column=0, padx=12, pady=4, sticky="w")

        ctk.CTkLabel(
            scroll,
            text=f"{q}{alerta}",
            width=120
        ).grid(row=i, column=1, padx=12, pady=4, sticky="w")

        win.protocol(
    "WM_DELETE_WINDOW",
    lambda: (win.destroy(), globals().__setitem__("janela_estoque", None))
)  

# ================= REGISTRO DE USO =================
def registrar_uso_material():
    global janela_uso

    if janela_uso and janela_uso.winfo_exists():
        janela_uso.lift()
        janela_uso.focus_force()
        return

    janela_uso = ctk.CTkToplevel(janela_principal)
    win = janela_uso

    win.title("Registrar Uso de Material")
    win.geometry("460x720")
    win.resizable(False, False)

    # 🔥 fica por cima do menu
    win.transient(janela_principal)  # prende à janela principal
    win.lift()
    win.attributes("-topmost", True)
    win.after(300, lambda: win.attributes("-topmost", False))
    win.focus_force()

    win.protocol(
        "WM_DELETE_WINDOW",
        lambda: (win.destroy(), globals().__setitem__("janela_uso", None))
    )

    scroll = ctk.CTkScrollableFrame(win)
    scroll.pack(expand=True, fill="both", padx=15, pady=15)

    ctk.CTkLabel(
        scroll,
        text="Registrar Uso de Material",
        font=("Arial", 18, "bold")
    ).pack(pady=10)

    msg = ctk.CTkLabel(scroll, text="", text_color="red")
    msg.pack(pady=5)

    # ================= VARIÁVEIS =================
    maquina_sel = ctk.StringVar()
    produto_sel = ctk.StringVar()
    numero_confirmado = ctk.BooleanVar(value=False)

    # ================= MÁQUINA =================
    ctk.CTkLabel(scroll, text="Máquina", font=("Arial", 14, "bold"))\
        .pack(anchor="w", padx=10)

    lista_maquinas = ctk.CTkScrollableFrame(scroll, height=140)
    lista_maquinas.pack(fill="x", padx=10, pady=5)

    maquina_sel = ctk.StringVar()
    botoes_maquinas = []

    def carregar_maquinas():
        for w in lista_maquinas.winfo_children():
            w.destroy()
        botoes_maquinas.clear()

        conn = conectar_db()
        c = conn.cursor()
        c.execute("SELECT nome FROM maquinas ORDER BY nome")
        maquinas = [m[0] for m in c.fetchall()]
        conn.close()

        for m in maquinas:
            btn = ctk.CTkButton(
                lista_maquinas,
                text=m,
                height=32,
                anchor="w",
                command=lambda n=m: selecionar_maquina(n)
            )
            btn.pack(fill="x", pady=2)
            botoes_maquinas.append(btn)

    def selecionar_maquina(nome):
        maquina_sel.set(nome)
        for b in botoes_maquinas:
            b.configure(state="disabled")
        msg.configure(text=f"Máquina selecionada: {nome}", text_color="white")

    carregar_maquinas()

    # ===== ADICIONAR NOVA MÁQUINA =====
    ctk.CTkLabel(scroll, text="Nova máquina").pack(anchor="w", padx=10, pady=(10, 0))

    entrada_nova_maquina = ctk.CTkEntry(
        scroll,
        placeholder_text="Nome da nova máquina"
    )
    entrada_nova_maquina.pack(fill="x", padx=10, pady=5)

    def adicionar_maquina():
        nome = entrada_nova_maquina.get().strip().lower()

        if not nome:
            msg.configure(text="Informe o nome da máquina", text_color="red")
            return

        conn = conectar_db()
        c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO maquinas VALUES (?)", (nome,))
        conn.commit()
        conn.close()

        entrada_nova_maquina.delete(0, "end")
        msg.configure(text="Máquina adicionada com sucesso", text_color="green")
        carregar_maquinas()

    ctk.CTkButton(
        scroll,
        text="➕ Adicionar máquina",
        height=36,
        fg_color="#2b9348",
        command=adicionar_maquina
    ).pack(fill="x", padx=10, pady=(0, 15))
    # ================= NÚMERO DA MÁQUINA =================
    ctk.CTkLabel(scroll, text="Número da máquina",
                 font=("Arial", 14, "bold"))\
        .pack(anchor="w", padx=10, pady=(10, 0))

    entrada_numero = ctk.CTkEntry(scroll, placeholder_text="Ex: 23")
    entrada_numero.pack(fill="x", padx=10, pady=5)

    def confirmar_numero():
        if not maquina_sel.get():
            msg.configure(text="Selecione a máquina primeiro", text_color="red")
            return

        numero = entrada_numero.get().strip()
        if not numero.isdigit():
            msg.configure(text="Número inválido", text_color="red")
            return

        entrada_numero.configure(state="disabled")
        numero_confirmado.set(True)
        msg.configure(text=f"Número confirmado: {numero}", text_color="white")

    ctk.CTkButton(
        scroll,
        text="Confirmar número da máquina",
        height=36,
        command=confirmar_numero
    ).pack(fill="x", padx=10, pady=(0, 10))

    # ================= PRODUTO =================
    ctk.CTkLabel(scroll, text="Produto",
                 font=("Arial", 14, "bold"))\
        .pack(anchor="w", padx=10)

    lista_produtos = ctk.CTkScrollableFrame(scroll, height=140)
    lista_produtos.pack(fill="x", padx=10, pady=5)

    conn = conectar_db()
    c = conn.cursor()
    c.execute("SELECT produto FROM estoque ORDER BY produto")
    produtos = [p[0] for p in c.fetchall()]
    conn.close()

    botoes_produtos = []

    def selecionar_produto(nome):
        if not numero_confirmado.get():
            msg.configure(
                text="Confirme o número da máquina primeiro",
                text_color="red"
            )
            return

        produto_sel.set(nome)
        for b in botoes_produtos:
            b.configure(state="disabled")
        msg.configure(text=f"Produto selecionado: {nome}", text_color="white")

    for p in produtos:
        btn = ctk.CTkButton(
            lista_produtos, text=p, height=32, anchor="w",
            command=lambda n=p: selecionar_produto(n)
        )
        btn.pack(fill="x", pady=2)
        botoes_produtos.append(btn)

    # ================= QUANTIDADE =================
    ctk.CTkLabel(scroll, text="Quantidade",
                 font=("Arial", 14, "bold"))\
        .pack(anchor="w", padx=10, pady=(10, 0))

    entrada_qtd = ctk.CTkEntry(scroll)
    entrada_qtd.insert(0, "1")
    entrada_qtd.pack(fill="x", padx=10, pady=5)

    def usar_quantidade_1():
        entrada_qtd.configure(state="normal")
        entrada_qtd.delete(0, "end")
        entrada_qtd.insert(0, "1")

    ctk.CTkButton(
        scroll,
        text="Usar quantidade padrão (1)",
        height=36,
        command=usar_quantidade_1
    ).pack(fill="x", padx=10, pady=(0, 10))

    # ================= DATA =================
    from datetime import datetime
    data_uso = datetime.now().strftime("%d-%m-%y")

    if usuario_logado["permissao"] == "admin":
        ctk.CTkLabel(scroll, text="Data (admin)").pack(anchor="w", padx=10)
        entrada_data = ctk.CTkEntry(scroll)
        entrada_data.insert(0, data_uso)
        entrada_data.pack(fill="x", padx=10, pady=5)
    else:
        entrada_data = None
        ctk.CTkLabel(scroll, text=f"Data do uso: {data_uso}")\
            .pack(anchor="w", padx=10, pady=10)

    # ================= SALVAR =================
    def salvar_uso():
        # Validações básicas
        if not maquina_sel.get() or not produto_sel.get() or not numero_confirmado.get():
            msg.configure(text="Preencha todas as etapas", text_color="red")
            return

        if not entrada_qtd.get().isdigit():
            msg.configure(text="Quantidade inválida", text_color="red")
            return

        qtd = int(entrada_qtd.get())
        data = entrada_data.get() if entrada_data else data_uso
        produto = produto_sel.get()

        conn = conectar_db()
        c = conn.cursor()

        # 🔎 Verifica estoque atual
        c.execute(
            "SELECT quantidade FROM estoque WHERE produto = ?",
            (produto,)
        )
        resultado = c.fetchone()

        if not resultado:
            conn.close()
            msg.configure(text="Produto não encontrado no estoque", text_color="red")
            return

        estoque_atual = resultado[0]

        if estoque_atual < qtd:
            conn.close()
            msg.configure(
                text=f"Estoque insuficiente! Disponível: {estoque_atual}",
                text_color="red"
            )
            return

        # ➖ Subtrai do estoque
        c.execute(
            "UPDATE estoque SET quantidade = quantidade - ? WHERE produto = ?",
            (qtd, produto)
        )

        # 💾 Registra o uso
        c.execute("""
            INSERT INTO uso_material
            (data, maquina, numero_maquina, produto, quantidade, usuario)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            data,
            maquina_sel.get(),
            entrada_numero.get(),
            produto,
            qtd,
            usuario_logado["nome"]
        ))

        conn.commit()
        conn.close()

        msg.configure(text="Uso registrado e estoque atualizado", text_color="green")

    # 🔘 BOTÃO SALVAR (AGORA APARECE)
    ctk.CTkButton(
        scroll,
        text="Salvar Uso de Material",
        height=42,
        fg_color="#1f6aa5",
        command=salvar_uso
    ).pack(fill="x", padx=10, pady=(15, 20))
#======================= Registro reparo ====================================

def registrar_reparo():
    global janela_reparo

    if janela_reparo and janela_reparo.winfo_exists():
        janela_reparo.lift()
        janela_reparo.focus_force()
        return

    janela_reparo = ctk.CTkToplevel(janela_principal)
    win = janela_reparo

    win.title("Registrar Reparo")
    win.geometry("460x720")
    win.resizable(False, False)

    # 🔥 fica por cima do menu
    win.transient(janela_principal)  # prende à janela principal
    win.lift()
    win.attributes("-topmost", True)
    win.after(300, lambda: win.attributes("-topmost", False))
    win.focus_force()

    win.protocol(
        "WM_DELETE_WINDOW",
        lambda: (win.destroy(), globals().__setitem__("janela_reparo", None))
    )

    scroll = ctk.CTkScrollableFrame(win)
    scroll.pack(expand=True, fill="both", padx=15, pady=15)

    ctk.CTkLabel(
        scroll,
        text="Registrar Reparo",
        font=("Arial", 18, "bold")
    ).pack(pady=10)

    msg = ctk.CTkLabel(scroll, text="", text_color="red")
    msg.pack(pady=5)

    # ================= VARIÁVEIS =================
    maquina_sel = ctk.StringVar()
    produto_sel = ctk.StringVar()
    numero_confirmado = ctk.BooleanVar(value=False)

    # ================= MÁQUINA =================
    ctk.CTkLabel(scroll, text="Máquina", font=("Arial", 14, "bold"))\
        .pack(anchor="w", padx=10)

    lista_maquinas = ctk.CTkScrollableFrame(scroll, height=140)
    lista_maquinas.pack(fill="x", padx=10, pady=5)

    maquina_sel = ctk.StringVar()
    botoes_maquinas = []

    def carregar_maquinas():
        for w in lista_maquinas.winfo_children():
            w.destroy()
        botoes_maquinas.clear()

        conn = conectar_db()
        c = conn.cursor()
        c.execute("SELECT nome FROM maquinas ORDER BY nome")
        maquinas = [m[0] for m in c.fetchall()]
        conn.close()

        for m in maquinas:
            btn = ctk.CTkButton(
                lista_maquinas,
                text=m,
                height=32,
                anchor="w",
                command=lambda n=m: selecionar_maquina(n)
            )
            btn.pack(fill="x", pady=2)
            botoes_maquinas.append(btn)

    def selecionar_maquina(nome):
        maquina_sel.set(nome)
        for b in botoes_maquinas:
            b.configure(state="disabled")
        msg.configure(text=f"Máquina selecionada: {nome}", text_color="white")

    carregar_maquinas()

    # ===== ADICIONAR NOVA MÁQUINA =====
    ctk.CTkLabel(scroll, text="Nova máquina").pack(anchor="w", padx=10, pady=(10, 0))

    entrada_nova_maquina = ctk.CTkEntry(
        scroll,
        placeholder_text="Nome da nova máquina"
    )
    entrada_nova_maquina.pack(fill="x", padx=10, pady=5)

    def adicionar_maquina():
        nome = entrada_nova_maquina.get().strip().lower()

        if not nome:
            msg.configure(text="Informe o nome da máquina", text_color="red")
            return

        conn = conectar_db()
        c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO maquinas VALUES (?)", (nome,))
        conn.commit()
        conn.close()

        entrada_nova_maquina.delete(0, "end")
        msg.configure(text="Máquina adicionada com sucesso", text_color="green")
        carregar_maquinas()

    ctk.CTkButton(
        scroll,
        text="➕ Adicionar máquina",
        height=36,
        fg_color="#2b9348",
        command=adicionar_maquina
    ).pack(fill="x", padx=10, pady=(0, 15))
    # ================= NÚMERO DA MÁQUINA =================
    ctk.CTkLabel(scroll, text="Número da máquina",
                 font=("Arial", 14, "bold"))\
        .pack(anchor="w", padx=10, pady=(10, 0))

    entrada_numero = ctk.CTkEntry(scroll, placeholder_text="Ex: 23")
    entrada_numero.pack(fill="x", padx=10, pady=5)

    def confirmar_numero():
        if not maquina_sel.get():
            msg.configure(text="Selecione a máquina primeiro", text_color="red")
            return

        numero = entrada_numero.get().strip()
        if not numero.isdigit():
            msg.configure(text="Número inválido", text_color="red")
            return

        entrada_numero.configure(state="disabled")
        numero_confirmado.set(True)
        msg.configure(text=f"Número confirmado: {numero}", text_color="white")

    ctk.CTkButton(
        scroll,
        text="Confirmar número da máquina",
        height=36,
        command=confirmar_numero
    ).pack(fill="x", padx=10, pady=(0, 10))

    # ================= PRODUTO =================
    ctk.CTkLabel(scroll, text="Produto",
                 font=("Arial", 14, "bold"))\
        .pack(anchor="w", padx=10)

    lista_produtos = ctk.CTkScrollableFrame(scroll, height=140)
    lista_produtos.pack(fill="x", padx=10, pady=5)

    conn = conectar_db()
    c = conn.cursor()
    c.execute("SELECT produto FROM estoque ORDER BY produto")
    produtos = [p[0] for p in c.fetchall()]
    conn.close()

    botoes_produtos = []

    def selecionar_produto(nome):
        if not numero_confirmado.get():
            msg.configure(
                text="Confirme o número da máquina primeiro",
                text_color="red"
            )
            return

        produto_sel.set(nome)
        for b in botoes_produtos:
            b.configure(state="disabled")
        msg.configure(text=f"Produto selecionado: {nome}", text_color="white")

    for p in produtos:
        btn = ctk.CTkButton(
            lista_produtos, text=p, height=32, anchor="w",
            command=lambda n=p: selecionar_produto(n)
        )
        btn.pack(fill="x", pady=2)
        botoes_produtos.append(btn)

    # ================= QUANTIDADE =================
    ctk.CTkLabel(scroll, text="Quantidade",
                 font=("Arial", 14, "bold"))\
        .pack(anchor="w", padx=10, pady=(10, 0))

    entrada_qtd = ctk.CTkEntry(scroll)
    entrada_qtd.insert(0, "1")
    entrada_qtd.pack(fill="x", padx=10, pady=5)

    def usar_quantidade_1():
        entrada_qtd.configure(state="normal")
        entrada_qtd.delete(0, "end")
        entrada_qtd.insert(0, "1")

    ctk.CTkButton(
        scroll,
        text="Usar quantidade padrão (1)",
        height=36,
        command=usar_quantidade_1
    ).pack(fill="x", padx=10, pady=(0, 10))

    # ================= DATA =================
    from datetime import datetime
    data_uso = datetime.now().strftime("%d-%m-%y")

    if usuario_logado["permissao"] == "admin":
        ctk.CTkLabel(scroll, text="Data (admin)").pack(anchor="w", padx=10)
        entrada_data = ctk.CTkEntry(scroll)
        entrada_data.insert(0, data_uso)
        entrada_data.pack(fill="x", padx=10, pady=5)
    else:
        entrada_data = None
        ctk.CTkLabel(scroll, text=f"Data do uso: {data_uso}")\
            .pack(anchor="w", padx=10, pady=10)

    # ================= SALVAR =================
    def salvar_uso():
        if not maquina_sel.get() or not produto_sel.get() or not numero_confirmado.get():
            msg.configure(text="Preencha todas as etapas", text_color="red")
            return

        data = entrada_data.get() if entrada_data else data_uso

        conn = conectar_db()
        c = conn.cursor()

        c.execute("""
            INSERT INTO reparos
            (data, maquina, numero_maquina, produto, quantidade, usuario)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            data,
            maquina_sel.get(),
            entrada_numero.get(),
            produto_sel.get(),
            1,  # 🔒 sempre 1
            usuario_logado["nome"]
        ))

        conn.commit()
        conn.close()

        msg.configure(text="Reparo registrado com sucesso", text_color="green")

    # 🔘 BOTÃO SALVAR (AGORA APARECE)
    ctk.CTkButton(
        scroll,
        text="Salvar Uso de Material",
        height=42,
        fg_color="#1f6aa5",
        command=salvar_uso
    ).pack(fill="x", padx=10, pady=(15, 20))
    
# ======================  aqui zera todo o registro  ========================

def zerar_registros():
    if usuario_logado["permissao"] != "master":
        messagebox.showerror(
            "Acesso negado",
            "Apenas o usuário MASTER pode zerar os registros."
        )
        return

    if not messagebox.askyesno(
        "Confirmação",
        "Isso vai apagar TODOS os registros (Trocas + Reparos).\nDeseja continuar?"
    ):
        return

    conn = conectar_db()
    c = conn.cursor()

    # apaga trocas
    c.execute("DELETE FROM uso_material")

    # apaga reparos  ← NOVO
    c.execute("DELETE FROM reparos")

    conn.commit()
    conn.close()

    messagebox.showinfo("OK", "Todos os registros foram zerados com sucesso.")

# ================= REGISTRO GERAL =================
def registro_geral():
    global janela_registro

    if janela_registro and janela_registro.winfo_exists():
        janela_registro.lift()
        janela_registro.focus_force()
        return

    janela_registro = ctk.CTkToplevel()
    win = janela_registro
    win.title("Registro Geral")
    win.geometry("1020x620")

    win.lift()
    win.focus_force()
    win.attributes("-topmost", True)
    win.after(200, lambda: win.attributes("-topmost", False))

    win.grid_rowconfigure(2, weight=1)
    win.grid_columnconfigure(0, weight=1)

    win.protocol(
        "WM_DELETE_WINDOW",
        lambda: (win.destroy(), globals().__setitem__("janela_registro", None))
    )

    # ================= FILTRO AVANÇADO =================
    frame_filtro = ctk.CTkFrame(win)
    frame_filtro.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
    frame_filtro.grid_columnconfigure((1, 3, 5), weight=1)

    ctk.CTkLabel(frame_filtro, text="Máquina").grid(row=0, column=0, padx=5)
    entrada_maquina = ctk.CTkEntry(frame_filtro)
    entrada_maquina.grid(row=0, column=1, padx=5, sticky="ew")

    ctk.CTkLabel(frame_filtro, text="Nº").grid(row=0, column=2, padx=5)
    entrada_numero = ctk.CTkEntry(frame_filtro, width=80)
    entrada_numero.grid(row=0, column=3, padx=5, sticky="w")

    ctk.CTkLabel(frame_filtro, text="Produto").grid(row=0, column=4, padx=5)
    entrada_produto = ctk.CTkEntry(frame_filtro)
    entrada_produto.grid(row=0, column=5, padx=5, sticky="ew")

    ctk.CTkLabel(frame_filtro, text="Data Inicial").grid(row=1, column=0, padx=5)
    entrada_data_ini = ctk.CTkEntry(frame_filtro, placeholder_text="DD-MM-YYYY")
    entrada_data_ini.grid(row=1, column=1, padx=5, sticky="ew")

    ctk.CTkLabel(frame_filtro, text="Data Final").grid(row=1, column=2, padx=5)
    entrada_data_fim = ctk.CTkEntry(frame_filtro, placeholder_text="DD-MM-YYYY")
    entrada_data_fim.grid(row=1, column=3, padx=5, sticky="ew")

    # ================= BOTÕES =================
    def pesquisar():
        carregar_dados()

    def limpar():
        for e in (entrada_maquina, entrada_numero, entrada_produto,
                  entrada_data_ini, entrada_data_fim):
            e.delete(0, "end")
        carregar_dados()

        # ENTER executa pesquisa (máquina, nº, produto, datas)
    for campo in (
        entrada_maquina,
        entrada_numero,
        entrada_produto,
        entrada_data_ini,
        entrada_data_fim
    ):
        campo.bind("<Return>", lambda e: pesquisar())

    win.bind("<Escape>", lambda e: limpar())

    ctk.CTkButton(frame_filtro, text="Pesquisar", command=pesquisar)\
        .grid(row=1, column=4, padx=5)

    ctk.CTkButton(frame_filtro, text="Limpar", command=limpar)\
        .grid(row=1, column=5, padx=5)

    # ================= TABELA =================
    scroll = ctk.CTkScrollableFrame(win)
    scroll.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

    headers = ["Data", "Máquina", "Nº", "Produto", "Qtd", "Tipo", "Usuário"]
    widths = [110, 150, 60, 180, 60, 80, 120]

    # ================= RESUMO =================
    frame_resumo = ctk.CTkFrame(win)
    frame_resumo.grid(row=3, column=0, padx=10, pady=(0, 10), sticky="ew")

    lbl_resumo = ctk.CTkLabel(frame_resumo, text="", font=("Arial", 13, "bold"))
    lbl_resumo.pack(anchor="w", padx=10, pady=8)

    def carregar_dados():
        for w in scroll.winfo_children():
            w.destroy()

        for col, h in enumerate(headers):
            ctk.CTkLabel(
                scroll,
                text=h,
                font=("Arial", 13, "bold"),
                width=widths[col]
            ).grid(row=0, column=col, padx=12, pady=8, sticky="w")

        filtros = []
        params = []

        if entrada_maquina.get():
            filtros.append("maquina LIKE ?")
            params.append(f"%{entrada_maquina.get()}%")

        if entrada_numero.get():
            filtros.append("numero_maquina LIKE ?")
            params.append(f"%{entrada_numero.get()}%")

        if entrada_produto.get():
            filtros.append("produto LIKE ?")
            params.append(f"%{entrada_produto.get()}%")

        if entrada_data_ini.get():
            filtros.append("substr(data,7,4)||substr(data,4,2)||substr(data,1,2) >= ?")
            params.append(
                entrada_data_ini.get()[6:10] +
                entrada_data_ini.get()[3:5] +
                entrada_data_ini.get()[0:2]
            )

        if entrada_data_fim.get():
            filtros.append("substr(data,7,4)||substr(data,4,2)||substr(data,1,2) <= ?")
            params.append(
                entrada_data_fim.get()[6:10] +
                entrada_data_fim.get()[3:5] +
                entrada_data_fim.get()[0:2]
            )

        where = "WHERE " + " AND ".join(filtros) if filtros else ""

        conn = conectar_db()
        c = conn.cursor()

        c.execute(f"""
            SELECT data, maquina, numero_maquina, produto, quantidade,
                'TROCA' AS tipo, usuario
            FROM uso_material
            {where}

            UNION ALL

            SELECT data, maquina, numero_maquina, produto, quantidade,
                'REPARO' AS tipo, usuario
            FROM reparos
            {where}

            ORDER BY data DESC
        """, params * 2)

        dados = c.fetchall()

        for i, linha in enumerate(dados, start=1):
            for col, valor in enumerate(linha):
                ctk.CTkLabel(
                    scroll,
                    text=str(valor),
                    width=widths[col]
                ).grid(row=i, column=col, padx=12, pady=4, sticky="w")

        # ===== RESUMO POR MÁQUINA =====
        c.execute(f"""
            SELECT maquina, numero_maquina, produto, tipo,
                COUNT(*),
                SUM(quantidade)
            FROM (
                SELECT maquina, numero_maquina, produto,
                    'TROCA' AS tipo, quantidade
                FROM uso_material
                {where}

                UNION ALL

                SELECT maquina, numero_maquina, produto,
                    'REPARO' AS tipo, quantidade
                FROM reparos
                {where}
            )
            GROUP BY maquina, numero_maquina, produto, tipo
        """, params * 2)

        resumo = c.fetchall()
        conn.close()

        texto = "Resumo por máquina:\n"
        for m, n, p, t, total, qtd in resumo:
            texto += f"• {m} ({n}) | {t} | Produto: {p} → {total} registros\n"

        lbl_resumo.configure(text=texto if resumo else "Nenhum registro encontrado.")

    carregar_dados()

# ================= RESUMO DE CONSUMO =================
def resumo_consumo_app():
    global janela_resumo

    if janela_resumo and janela_resumo.winfo_exists():
        janela_resumo.lift()
        janela_resumo.focus_force()
        return

    conn = conectar_db()
    c = conn.cursor()

    c.execute("""
        SELECT produto, COALESCE(SUM(quantidade), 0)
        FROM uso_material
        GROUP BY produto
        ORDER BY produto
    """)

    dados = c.fetchall()
    conn.close()

    janela_resumo = ctk.CTkToplevel()
    win = janela_resumo
    win.title("Resumo de Consumo por Item")
    win.geometry("450x420")

    win.lift()
    win.focus_force()
    win.attributes("-topmost", True)
    win.after(200, lambda: win.attributes("-topmost", False))
    #win.grab_set() # menu so se fechar a janela

    win.grid_rowconfigure(0, weight=1)
    win.grid_columnconfigure(0, weight=1)

    scroll = ctk.CTkScrollableFrame(win, width=420, height=380)
    scroll.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

    # Cabeçalhos
    headers = ["Produto", "Total Usado"]
    for col, h in enumerate(headers):
        ctk.CTkLabel(
            scroll,
            text=h,
            font=("Arial", 13, "bold"),
            width=220 if col == 0 else 120
        ).grid(row=0, column=col, padx=12, pady=8, sticky="w")

    # Dados
    for i, (produto, total) in enumerate(dados, start=1):
        ctk.CTkLabel(
            scroll,
            text=produto,
            width=220
        ).grid(row=i, column=0, padx=12, pady=4, sticky="w")

        ctk.CTkLabel(
            scroll,
            text=str(total),
            width=120
        ).grid(row=i, column=1, padx=12, pady=4, sticky="w")

    win.protocol(
    "WM_DELETE_WINDOW",
    lambda: (win.destroy(), globals().__setitem__("janela_resumo", None))
)

# ================= WEB =================
app = Flask(__name__)
app.secret_key = "segredo"

HTML_BASE = """
<!doctype html>
<html lang="pt-br">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Sistema de Estoque</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-dark text-light">

<nav class="navbar navbar-expand-lg navbar-dark bg-black">
  <div class="container-fluid">
    <a class="navbar-brand" href="/estoque">Estoque</a>
    <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#menu">
      <span class="navbar-toggler-icon"></span>
    </button>
    <div class="collapse navbar-collapse" id="menu">
      <ul class="navbar-nav ms-auto">
        <li class="nav-item"><a class="nav-link" href="/estoque">Estoque</a></li>
        <li class="nav-item"><a class="nav-link" href="/registro">Registro</a></li>
        <li class="nav-item"><a class="nav-link text-danger" href="/logout">Sair</a></li>
      </ul>
    </div>
  </div>
</nav>

<div class="container mt-3">
{{ conteudo|safe }}
</div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def login_web():
    erro = ""
    if request.method == "POST":
        u = request.form["user"]
        s = request.form["pass"]

        conn = conectar_db()
        c = conn.cursor()
        c.execute("SELECT permissao FROM usuarios WHERE usuario=? AND senha=?", (u, s))
        r = c.fetchone()
        conn.close()

        if r:
            session["user"] = u
            return redirect("/estoque")
        erro = "Login inválido"

    conteudo = f"""
    <div class="card bg-secondary p-4 mx-auto" style="max-width:400px">
        <h3 class="text-center">Login</h3>
        <form method="post">
            <input class="form-control mb-2" name="user" placeholder="Usuário">
            <input class="form-control mb-2" name="pass" type="password" placeholder="Senha">
            <button class="btn btn-primary w-100">Entrar</button>
            <p class="text-danger mt-2">{erro}</p>
        </form>
    </div>
    """
    return render_template_string(HTML_BASE, conteudo=conteudo)

@app.route("/estoque")
def estoque_web():
    if "user" not in session:
        return redirect("/")

    conn = conectar_db()
    c = conn.cursor()
    c.execute("SELECT produto, quantidade FROM estoque ORDER BY produto")
    dados = c.fetchall()
    conn.close()

    linhas = "".join(
        f"<tr><td>{p}</td><td>{q}</td></tr>"
        for p, q in dados
    )

    conteudo = f"""
<h4 class="mb-3">📦 Estoque Atual</h4>

<div class="table-responsive">
<table class="table table-dark table-striped table-sm">
    <tr><th>Produto</th><th>Quantidade</th></tr>
    {linhas}
</table>
</div>

<a class="btn btn-info w-100 mb-2" href="/registro">
📑 Registro Geral
</a>

<a class="btn btn-info w-100 mb-2" href="/resumo">
📊 Resumo de Consumo
</a>

<a class="btn btn-secondary w-100 mt-2" href="/logout">
🚪 Sair
</a>
"""
    return render_template_string(HTML_BASE, conteudo=conteudo)


@app.route("/registro", methods=["GET", "POST"])
def registro_web():
    if "user" not in session:
        return redirect("/")

    maquina = request.form.get("maquina", "")
    numero = request.form.get("numero", "")
    produto = request.form.get("produto", "")

    filtros = []
    params = []

    if maquina:
        filtros.append("maquina LIKE ?")
        params.append(f"%{maquina}%")

    if numero:
        filtros.append("numero_maquina LIKE ?")
        params.append(f"%{numero}%")

    if produto:
        filtros.append("produto LIKE ?")
        params.append(f"%{produto}%")

    where = "WHERE " + " AND ".join(filtros) if filtros else ""

    conn = conectar_db()
    c = conn.cursor()

    # ===== REGISTROS =====
    c.execute(f"""
        SELECT data, maquina, numero_maquina, produto, quantidade, usuario
        FROM uso_material
        {where}
        ORDER BY data DESC
    """, params)

    dados = c.fetchall()

    linhas = "".join(
        f"""
        <tr>
            <td>{d}</td>
            <td>{m}</td>
            <td>{n}</td>
            <td>{p}</td>
            <td>{q}</td>
            <td>{u}</td>
        </tr>
        """
        for d, m, n, p, q, u in dados
    )

    # ===== RESUMO POR MÁQUINA =====
    c.execute(f"""
        SELECT maquina, numero_maquina, produto,
               COUNT(*),
               SUM(quantidade)
        FROM uso_material
        {where}
        GROUP BY maquina, numero_maquina, produto
        ORDER BY maquina, numero_maquina
    """, params)

    resumo = c.fetchall()
    conn.close()

    resumo_html = "<h5 class='mt-4'>📊 Resumo por Máquina</h5>"
    if resumo:
        resumo_html += "<ul class='list-group list-group-flush'>"
        for m, n, p, total, qtd in resumo:
            resumo_html += f"""
            <li class="list-group-item bg-dark text-light">
                • <b>{m} ({n})</b> | Produto: {p}
                → {total} registros | Troca: {qtd or 0}
            </li>
            """
        resumo_html += "</ul>"
    else:
        resumo_html += "<p>Nenhum registro encontrado.</p>"

    conteudo = f"""
    <h4 class="mb-3">📑 Registro Geral</h4>

    <form method="post" class="row g-2 mb-3">
        <div class="col-md-3">
            <input class="form-control" name="maquina" placeholder="Máquina">
        </div>
        <div class="col-md-2">
            <input class="form-control" name="numero" placeholder="Nº">
        </div>
        <div class="col-md-3">
            <input class="form-control" name="produto" placeholder="Produto">
        </div>
        <div class="col-md-2">
            <button class="btn btn-primary w-100">Pesquisar</button>
        </div>
        <div class="col-md-2">
            <a class="btn btn-secondary w-100" href="/registro">Limpar</a>
        </div>
    </form>

    <div class="table-responsive">
    <table class="table table-dark table-striped table-sm">
        <tr>
            <th>Data</th>
            <th>Máquina</th>
            <th>Nº</th>
            <th>Produto</th>
            <th>Qtd</th>
            <th>Usuário</th>
        </tr>
        {linhas}
    </table>
    </div>

    {resumo_html}
    """

    return render_template_string(HTML_BASE, conteudo=conteudo)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

def iniciar_web(modo_cloud=False):
    import os

    def run():
        port = int(os.environ.get("PORT", 5000))

        app.run(
            host="0.0.0.0",
            port=port,
            debug=False,
            use_reloader=False
        )

    # ☁️ Cloud (Render)
    if modo_cloud:
        run()
        return

    # 💻 Desktop (como já era)
    threading.Thread(target=run, daemon=True).start()

    messagebox.showinfo(
        "Interface Web",
        "Servidor iniciado!\n\nAcesse pelo celular:\nhttp://IP_DO_PC:5000"
    )

@app.route("/resumo")
def resumo_web():
    if "user" not in session:
        return redirect("/")

    conn = conectar_db()
    c = conn.cursor()

    c.execute("""
        SELECT produto, SUM(quantidade)
        FROM uso_material
        GROUP BY produto
        ORDER BY produto
    """)

    dados = c.fetchall()
    conn.close()

    linhas = "".join(
        f"<tr><td>{p}</td><td>{t}</td></tr>"
        for p, t in dados
    )

    conteudo = f"""
    <h4 class="mb-3">📊 Resumo de Consumo por Item</h4>

    <div class="table-responsive">
    <table class="table table-dark table-striped table-sm">
        <tr>
            <th>Produto</th>
            <th>Total Usado</th>
        </tr>
        {linhas}
    </table>
    </div>

    <a class="btn btn-secondary mt-3 w-100" href="/estoque">Voltar</a>
    """
    return render_template_string(HTML_BASE, conteudo=conteudo)
#===================touche=========================

def detectar_modo_touch(app):
    largura = app.winfo_screenwidth()
    altura = app.winfo_screenheight()

    # telas pequenas / tablet / touch
    if largura <= 1366 or altura <= 768:
        return True
    return False

# ================= GUI =================
def iniciar():
    criar_tabelas()
    global janela_principal
    janela_principal = ctk.CTk()
    app = janela_principal

    app.title("Sistema de Estoque")
    app.geometry("420x640")
    app.resizable(False, False)

    app.update_idletasks()

    modo_touch = detectar_modo_touch(app)

    if modo_touch:
        ctk.set_widget_scaling(1.0)
        app.geometry("480x720")
    else:
        ctk.set_widget_scaling(1.0)
        app.geometry("420x640")

    # ================= UTIL =================
    def limpar_tela():
        for widget in app.winfo_children():
            widget.destroy()

    def botao(frame, texto, comando):
        ctk.CTkButton(
            frame,
            text=texto,
            command=comando,
            height=30,
            font=("Arial", 14, "bold"),
            corner_radius=12
        ).pack(fill="x", padx=50, pady=6)

    def botao_sair(frame, texto, comando):
        ctk.CTkButton(
            frame,
            text=texto,
            command=comando,
            height=30,
            font=("Arial", 14, "bold"),
            fg_color="#8b0000",
            hover_color="#a30000",
            corner_radius=12
        ).pack(fill="x", padx=40, pady=16)

    # ================= LOGIN =================
    def tela_login():
        limpar_tela()

        frame = ctk.CTkFrame(app, fg_color="transparent")
        frame.pack(expand=True, pady=80)

        ctk.CTkLabel(
            frame,
            text="Sistema de Estoque",
            font=("Arial", 22, "bold")
        ).pack(pady=(40, 20))

        entrada_usuario = ctk.CTkEntry(
            frame,
            placeholder_text="Usuário",
            width=320,
            height=50,
            font=("Arial", 15)
        )
        entrada_usuario.pack(pady=12)

        entrada_senha = ctk.CTkEntry(
            frame,
            placeholder_text="Senha",
            show="*",
            width=320,
            height=50,
            font=("Arial", 15)
        )
        entrada_senha.pack(pady=12)

        msg = ctk.CTkLabel(frame, text="", text_color="red")
        msg.pack(pady=10)

        def entrar(event=None):
            usuario = entrada_usuario.get().strip()
            senha = entrada_senha.get().strip()

            if not usuario or not senha:
                msg.configure(text="Informe usuário e senha")
                return

            conn = conectar_db()
            c = conn.cursor()
            c.execute(
                "SELECT permissao FROM usuarios WHERE usuario=? AND senha=?",
                (usuario, senha)
            )
            resultado = c.fetchone()
            conn.close()

            if not resultado:
                msg.configure(text="Usuário ou senha inválidos")
                return

            usuario_logado["nome"] = usuario
            usuario_logado["permissao"] = resultado[0]

            tela_menu()

        # ENTER FUNCIONA
        entrada_usuario.bind("<Return>", entrar)
        entrada_senha.bind("<Return>", entrar)

        ctk.CTkButton(
            frame,
            text="Entrar",
            height=56,
            width=320,
            font=("Arial", 16, "bold"),
            fg_color="#1f6aa5",
            corner_radius=12,
            command=entrar
        ).pack(pady=24)

    # ================= MENU =================
    def tela_menu():
        limpar_tela()

        container = ctk.CTkFrame(app)
        container.pack(expand=True, fill="both")

        scroll = ctk.CTkScrollableFrame(container)
        scroll.pack(expand=True, fill="both", padx=10, pady=10)

        ctk.CTkLabel(
            scroll,
            text=f"Bem-vindo, {usuario_logado['nome']}",
            font=("Arial", 18, "bold")
        ).pack(pady=20)

        botao(scroll, "Adicionar Produto", adicionar_produto)
        botao(scroll, "Listar Estoque", listar_estoque)
        botao(scroll, "Registrar Troca", registrar_uso_material)
        botao(scroll, "Registrar Reparo", registrar_reparo)
        botao(scroll, "Registro Geral", registro_geral)
        if usuario_logado["permissao"] == "master":
            botao(scroll, "Zerar Registro", zerar_registros)
        botao(scroll, "Resumo de Consumo (Itens)", resumo_consumo_app)
        botao(scroll, "Trocar Senha", trocar_senha)

        if usuario_logado["permissao"] in ("admin", "master"):
            botao(scroll, "Criar Usuário", criar_usuario)
            botao(scroll, "Remover Usuário", remover_usuario)
        if usuario_logado["permissao"] == "master":
            botao(scroll, "Trocar Senha de Usuário (MASTER)", master_trocar_senha_usuario)
            botao(scroll, "Iniciar Interface Web", iniciar_web)
        botao_sair(scroll, "🚪 Sair", sair)
        

    # ================= SAIR =================
    def sair():
        usuario_logado["nome"] = ""
        usuario_logado["permissao"] = ""
        tela_login()

    tela_login()
    app.mainloop()

iniciar()
