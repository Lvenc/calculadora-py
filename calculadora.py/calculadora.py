import tkinter as tk
from tkinter import messagebox
import math
import re


class Calculadora:
    def __init__(self):
        self.janela = tk.Tk()
        self.setup_janela()
        self.setup_cores()
        self.setup_interface()
        self.historico = []

    def setup_janela(self):
        self.janela.title("Calculadora")
        self.janela.geometry("380x550")
        self.janela.config(bg="#1e1e2f")
        self.janela.resizable(False, False)
        self.janela.update_idletasks()
        x = (self.janela.winfo_screenwidth() // 2) - (380 // 2)
        y = (self.janela.winfo_screenheight() // 2) - (550 // 2)
        self.janela.geometry(f"380x550+{x}+{y}")

    def setup_cores(self):
        self.cores = {
            "fundo_principal": "#1e1e2f",
            "fundo_entrada": "#282c34",
            "fundo_botao": "#3a3f58",
            "operadores": "#ff9500",
            "clear": "#ff3b30",
            "equals": "#34c759",
            "texto": "#e6e6e6",
            "texto_branco": "#ffffff",
            "hover_numero": "#505770",
            "hover_operador": "#ffb347",
            "hover_clear": "#ff5c4d",
            "hover_equals": "#4cd964"
        }

    def setup_interface(self):
        self.criar_display()
        self.criar_botoes()
        self.configurar_teclas()

    def criar_display(self):
        self.frame_historico = tk.Frame(self.janela, bg=self.cores["fundo_entrada"], height=80)
        self.frame_historico.pack(padx=15, pady=(15, 5), fill="x")
        self.frame_historico.pack_propagate(False)

        self.label_historico = tk.Label(
            self.frame_historico,
            text="",
            font=("Consolas", 12),
            bg=self.cores["fundo_entrada"],
            fg="#888",
            anchor="e",
            justify="right"
        )
        self.label_historico.pack(fill="both", expand=True, padx=10, pady=5)

        self.frame_entrada = tk.Frame(self.janela, bg=self.cores["fundo_entrada"], bd=2, relief="ridge")
        self.frame_entrada.pack(padx=15, pady=(5, 15), fill="x")

        self.entrada = tk.Entry(
            self.frame_entrada,
            font=("Consolas", 28, "bold"),
            bg=self.cores["fundo_principal"],
            fg="#000000",
            bd=0,
            justify="right",
            insertbackground="#ffa500",
            state="readonly"
        )
        self.entrada.pack(padx=10, pady=15, fill="x")

        self.expressao_atual = ""
        self.atualizar_display()

    def criar_botoes(self):
        botoes_layout = [
            [("(", "operador"), (")", "operador"), ("%", "operador"), ("AC", "clear")],
            [("7", "numero"), ("8", "numero"), ("9", "numero"), ("÷", "operador")],
            [("4", "numero"), ("5", "numero"), ("6", "numero"), ("×", "operador")],
            [("1", "numero"), ("2", "numero"), ("3", "numero"), ("-", "operador")],
            [("0", "numero"), (".", "numero"), ("=", "equals"), ("+", "operador")]
        ]

        for i, linha in enumerate(botoes_layout):
            frame = tk.Frame(self.janela, bg=self.cores["fundo_principal"])
            frame.pack(expand=True, fill="both", padx=15, pady=3)

            if i == 4:
                self.criar_linha_especial(frame, linha)
            else:
                for botao_texto, tipo in linha:
                    self.criar_botao(frame, botao_texto, tipo)

    def criar_botao(self, frame, texto, tipo):
        config_cores = {
            "clear": (self.cores["clear"], self.cores["texto_branco"], self.cores["hover_clear"]),
            "backspace": (self.cores["clear"], self.cores["texto_branco"], self.cores["hover_clear"]),
            "operador": (self.cores["operadores"], self.cores["texto_branco"], self.cores["hover_operador"]),
            "funcao": (self.cores["operadores"], self.cores["texto_branco"], self.cores["hover_operador"]),
            "equals": (self.cores["equals"], self.cores["texto_branco"], self.cores["hover_equals"]),
            "numero": (self.cores["fundo_botao"], self.cores["texto"], self.cores["hover_numero"])
        }

        cor_fundo, cor_texto, cor_hover = config_cores.get(tipo, config_cores["numero"])

        btn = tk.Button(
            frame,
            text=texto,
            font=("Consolas", 20, "bold"),
            bg=cor_fundo,
            fg=cor_texto,
            activebackground=cor_hover,
            activeforeground=self.cores["texto_branco"],
            bd=0,
            relief="raised",
            cursor="hand2",
            command=lambda: self.processar_clique(texto)
        )
        btn.pack(side="left", expand=True, fill="both", padx=3, pady=3)
        btn.bind("<Enter>", lambda e: self.on_hover_enter(e, cor_hover))
        btn.bind("<Leave>", lambda e: self.on_hover_leave(e, cor_fundo))

    def criar_linha_especial(self, frame, linha):
        def criar_botao_simples(texto, cor_bg, cor_hover, comando):
            btn = tk.Button(
                frame,
                text=texto,
                font=("Consolas", 20, "bold"),
                bg=cor_bg,
                fg=self.cores["texto"],
                activebackground=cor_hover,
                activeforeground=self.cores["texto_branco"],
                bd=0,
                relief="raised",
                cursor="hand2",
                command=comando
            )
            btn.pack(side="left", expand=True, fill="both", padx=3, pady=3)
            btn.bind("<Enter>", lambda e: self.on_hover_enter(e, cor_hover))
            btn.bind("<Leave>", lambda e: self.on_hover_leave(e, cor_bg))

        criar_botao_simples("0", self.cores["fundo_botao"], self.cores["hover_numero"], lambda: self.processar_clique("0"))
        criar_botao_simples(".", self.cores["fundo_botao"], self.cores["hover_numero"], lambda: self.processar_clique("."))
        criar_botao_simples("=", self.cores["equals"], self.cores["hover_equals"], lambda: self.processar_clique("="))
        criar_botao_simples("+", self.cores["operadores"], self.cores["hover_operador"], lambda: self.processar_clique("+"))

    def on_hover_enter(self, event, cor_hover):
        event.widget.config(bg=cor_hover)

    def on_hover_leave(self, event, cor_original):
        event.widget.config(bg=cor_original)

    def configurar_teclas(self):
        self.janela.bind('<Key>', self.processar_tecla)
        self.janela.focus_set()

    def processar_tecla(self, event):
        tecla = event.keysym
        char = event.char

        if char.isdigit() or char in "+-*/().":
            self.processar_clique(char)
        elif tecla == "Return":
            self.processar_clique("=")
        elif tecla == "BackSpace":
            self.processar_clique("⌫")
        elif char.lower() in ["c", "a"]:
            self.processar_clique("AC")
        elif tecla == "Escape":
            self.processar_clique("CE")
        elif char == "*":
            self.processar_clique("×")
        elif char == "/":
            self.processar_clique("÷")

    def processar_clique(self, botao):
        if botao == "AC":
            self.limpar_tudo()
        elif botao == "CE":
            self.limpar_entrada()
        elif botao == "⌫":
            self.backspace()
        elif botao == "=":
            self.calcular()
        elif botao in "+-×÷^%":
            self.adicionar_operador(botao)
        elif botao in "()":
            self.adicionar_parenteses(botao)
        else:
            self.adicionar_numero(botao)

    def adicionar_numero(self, numero):
        if numero == "." and "." in self.obter_ultimo_numero():
            return
        self.expressao_atual += numero
        self.atualizar_display()

    def adicionar_operador(self, operador):
        if self.expressao_atual and self.expressao_atual[-1] not in "+-×÷^%":
            self.expressao_atual += operador
        elif self.expressao_atual:
            self.expressao_atual = self.expressao_atual[:-1] + operador
        self.atualizar_display()

    def adicionar_parenteses(self, parenteses):
        if parenteses == "(":
            if self.expressao_atual and (self.expressao_atual[-1].isdigit() or self.expressao_atual[-1] == ")"):
                self.expressao_atual += "×("
            else:
                self.expressao_atual += "("
        else:
            if self.expressao_atual.count("(") > self.expressao_atual.count(")"):
                self.expressao_atual += ")"
        self.atualizar_display()

    def obter_ultimo_numero(self):
        numeros = re.findall(r'\d*\.?\d*', self.expressao_atual)
        return numeros[-1] if numeros else ""

    def limpar_tudo(self):
        self.expressao_atual = ""
        self.atualizar_display()
        self.atualizar_historico("")

    def limpar_entrada(self):
        self.expressao_atual = ""
        self.atualizar_display()

    def backspace(self):
        if self.expressao_atual:
            self.expressao_atual = self.expressao_atual[:-1]
            self.atualizar_display()

    def calcular(self):
        if not self.expressao_atual:
            return
        try:
            expressao = self.preparar_expressao(self.expressao_atual)
            expressao = self.remover_zeros_a_esquerda(expressao)
            self.atualizar_historico(f"{self.expressao_atual} =")
            resultado = eval(expressao)
            if isinstance(resultado, float):
                resultado = int(resultado) if resultado.is_integer() else round(resultado, 10)
            self.expressao_atual = str(resultado)
            self.atualizar_display()
        except ZeroDivisionError:
            self.mostrar_erro("Erro: Divisão por zero")
        except Exception:
            self.mostrar_erro("Erro: Expressão inválida")

    def preparar_expressao(self, expressao):
        expressao = expressao.replace("×", "*").replace("÷", "/").replace("^", "**")
        expressao = self.processar_porcentagem(expressao)
        expressao = re.sub(r'\bsin\b', 'math.sin', expressao)
        expressao = re.sub(r'\bcos\b', 'math.cos', expressao)
        expressao = re.sub(r'\btan\b', 'math.tan', expressao)
        expressao = re.sub(r'\blog\b', 'math.log10', expressao)
        expressao = re.sub(r'\bln\b', 'math.log', expressao)
        return expressao

    def remover_zeros_a_esquerda(self, expressao):
        return re.sub(r'\b0+(\d+)', r'\1', expressao)

    def processar_porcentagem(self, expressao):
        if "%" not in expressao:
            return expressao
        padrao = r'(\d+(?:\.\d+)?)\s*([+\-*/])\s*(\d+(?:\.\d+)?)%'
        def substituir(match):
            num1 = float(match.group(1))
            operador = match.group(2)
            num2 = float(match.group(3))
            if operador in "+-":
                return f"{num1}{operador}{num1 * (num2 / 100)}"
            else:
                return f"{num1}{operador}{num2 / 100}"
        expressao = re.sub(padrao, substituir, expressao)
        return expressao.replace("%", "/100")

    def mostrar_erro(self, mensagem):
        self.expressao_atual = ""
        self.atualizar_display("Erro")
        self.janela.after(2000, lambda: self.atualizar_display())

    def atualizar_display(self, texto=None):
        if texto is None:
            texto = self.expressao_atual if self.expressao_atual else "0"
        self.entrada.config(state="normal")
        self.entrada.delete(0, tk.END)
        self.entrada.insert(0, texto)
        self.entrada.config(state="readonly")

    def atualizar_historico(self, texto):
        if texto:
            self.historico.append(texto)
            if len(self.historico) > 3:
                self.historico.pop(0)
        historico_texto = "\n".join(self.historico[-3:])
        self.label_historico.config(text=historico_texto)

    def executar(self):
        self.janela.mainloop()


if __name__ == "__main__":
    calculadora = Calculadora()
    calculadora.executar()
