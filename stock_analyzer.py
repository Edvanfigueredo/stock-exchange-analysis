"""
╔══════════════════════════════════════════════════════════════════╗
║           📈 Stock Exchange Analysis - Yahoo Finance  📉        ║
║              Análise de Ações com Painel Azul                    ║
╚══════════════════════════════════════════════════════════════════╝

Autor: Edvan Figuerêdo Araujo
GitHub: https://github.com/Edvanfigueredo
Versão: 1.0.0
"""

import sys
import time

try:
    import yfinance as yf
except ImportError:
    print("Instalando dependências...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "yfinance", "-q"])
    import yfinance as yf

try:
    from colorama import Fore, Back, Style, init
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "colorama", "-q"])
    from colorama import Fore, Back, Style, init

try:
    from tabulate import tabulate
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "tabulate", "-q"])
    from tabulate import tabulate

import datetime

init(autoreset=True)

# ─────────────────────────────────────────────
#  CORES DO PAINEL AZUL
# ─────────────────────────────────────────────
AZUL       = Fore.CYAN
AZUL_ESC   = Fore.BLUE
BRANCO     = Fore.WHITE
VERDE      = Fore.GREEN
VERMELHO   = Fore.RED
AMARELO    = Fore.YELLOW
CINZA      = Fore.LIGHTBLACK_EX
NEGRITO    = Style.BRIGHT
RESET      = Style.RESET_ALL
BG_AZUL    = Back.BLUE


def limpar_tela():
    import os
    os.system("cls" if os.name == "nt" else "clear")


def banner():
    print(f"""
╔═════════════════════════════════════════════════════════════════════════════════════╗
║  {AZUL}{NEGRITO}                                                      {AZUL}        ║
║  {BRANCO}📈  STOCK EXCHANGE ANALYSIS  •  Yahoo Finance  •  Análise de Ações  📉             ║
║  {CINZA}Consulte empresas e descubra se vale a pena investir agora!   {AZUL}        ║
║                                                                       {RESET}       ║
╚═════════════════════════════════════════════════════════════════════════════════════╝
""")


def loading_bar(msg="Consultando Yahoo Finance", total=30):
    print(f"\n{AZUL}{NEGRITO}{msg}...{RESET}")
    print(f"{AZUL}[", end="", flush=True)
    for i in range(total):
        time.sleep(0.03)
        print(f"{VERDE}█", end="", flush=True)
    print(f"{AZUL}] {VERDE}✓ Concluído!{RESET}\n")


def buscar_ticker(nome_empresa: str) -> str | None:
    """
    Tenta encontrar o ticker da empresa pelo nome.
    Retorna o ticker ou None se não encontrado.
    """
    # Dicionário com empresas brasileiras e internacionais populares
    empresas_conhecidas = {
        # Brasileiras
        "petrobras": "PETR4.SA", "vale": "VALE3.SA", "itaú": "ITUB4.SA",
        "itau": "ITUB4.SA", "bradesco": "BBDC4.SA", "banco do brasil": "BBAS3.SA",
        "ambev": "ABEV3.SA", "weg": "WEGE3.SA", "magazine luiza": "MGLU3.SA",
        "magalu": "MGLU3.SA", "nubank": "NU", "embraer": "EMBR3.SA",
        "localiza": "RENT3.SA", "totvs": "TOTS3.SA", "raia drogasil": "RADL3.SA",
        "suzano": "SUZB3.SA", "jbs": "JBSS3.SA", "gerdau": "GGBR4.SA",
        "b3": "B3SA3.SA", "cosan": "CSAN3.SA", "ultrapar": "UGPA3.SA",
        "eneva": "ENEV3.SA", "engie": "EGIE3.SA", "taesa": "TAEE11.SA",
        "eletrobras": "ELET3.SA", "copel": "CPLE6.SA", "sabesp": "SBSP3.SA",
        # Internacionais
        "apple": "AAPL", "microsoft": "MSFT", "google": "GOOGL",
        "alphabet": "GOOGL", "amazon": "AMZN", "tesla": "TSLA",
        "meta": "META", "facebook": "META", "netflix": "NFLX",
        "nvidia": "NVDA", "intel": "INTC", "amd": "AMD",
        "samsung": "005930.KS", "sony": "SONY", "ibm": "IBM",
        "paypal": "PYPL", "uber": "UBER", "airbnb": "ABNB",
        "spotify": "SPOT", "twitter": "X", "snapchat": "SNAP",
        "berkshire": "BRK-B", "jpmorgan": "JPM", "visa": "V",
        "mastercard": "MA", "coca cola": "KO", "pepsi": "PEP",
        "mcdonalds": "MCD", "disney": "DIS", "nike": "NKE",
        "boeing": "BA", "exxon": "XOM", "chevron": "CVX",
        "johnson": "JNJ", "pfizer": "PFE", "moderna": "MRNA",
    }

    nome_lower = nome_empresa.lower().strip()

    # Busca exata no dicionário
    for chave, ticker in empresas_conhecidas.items():
        if nome_lower == chave or nome_lower in chave or chave in nome_lower:
            return ticker

    # Tenta como ticker direto (ex: AAPL, PETR4.SA)
    return nome_empresa.upper().strip()


def calcular_recomendacao(info: dict, hist) -> tuple[str, float, str]:
    """
    Calcula uma pontuação de 0–100 e retorna (nível, score, justificativa).
    Baseado em: P/E ratio, 52w position, dividendos, crescimento.
    """
    score = 50.0
    fatores = []

    # 1. P/E Ratio (Preço/Lucro)
    pe = info.get("trailingPE") or info.get("forwardPE")
    if pe:
        if pe < 15:
            score += 15
            fatores.append(f"P/E baixo ({pe:.1f}) → ação barata ✓")
        elif pe < 25:
            score += 5
            fatores.append(f"P/E moderado ({pe:.1f}) → preço justo ~")
        elif pe < 40:
            score -= 5
            fatores.append(f"P/E alto ({pe:.1f}) → ação cara ✗")
        else:
            score -= 15
            fatores.append(f"P/E muito alto ({pe:.1f}) → risco elevado ✗")

    # 2. Posição no range 52 semanas
    low52  = info.get("fiftyTwoWeekLow", 0)
    high52 = info.get("fiftyTwoWeekHigh", 0)
    preco  = info.get("currentPrice") or info.get("regularMarketPrice", 0)

    if low52 and high52 and preco:
        pos = (preco - low52) / (high52 - low52) * 100
        if pos < 30:
            score += 15
            fatores.append(f"Próx. mínima 52sem ({pos:.0f}%) → oportunidade ✓")
        elif pos > 80:
            score -= 10
            fatores.append(f"Próx. máxima 52sem ({pos:.0f}%) → risco de correção ✗")
        else:
            fatores.append(f"Posição 52sem: {pos:.0f}% do intervalo ~")

    # 3. Dividend Yield
    dy = info.get("dividendYield", 0)
    if dy:
        dy_pct = dy * 100
        if dy_pct > 5:
            score += 10
            fatores.append(f"Dividend yield alto ({dy_pct:.2f}%) → renda passiva ✓")
        elif dy_pct > 2:
            score += 5
            fatores.append(f"Dividend yield ok ({dy_pct:.2f}%) ~")

    # 4. Crescimento de receita
    rg = info.get("revenueGrowth", 0)
    if rg:
        if rg > 0.10:
            score += 10
            fatores.append(f"Crescimento receita {rg*100:.1f}% → expansão ✓")
        elif rg < 0:
            score -= 10
            fatores.append(f"Queda de receita {rg*100:.1f}% → alerta ✗")

    # 5. Margem de lucro
    mg = info.get("profitMargins", 0)
    if mg:
        if mg > 0.20:
            score += 10
            fatores.append(f"Margem lucro alta ({mg*100:.1f}%) ✓")
        elif mg < 0:
            score -= 10
            fatores.append(f"Prejuízo líquido ({mg*100:.1f}%) ✗")

    score = max(0, min(100, score))

    if score >= 70:
        nivel = "🟢 COMPRAR"
        cor   = VERDE
    elif score >= 50:
        nivel = "🟡 NEUTRO"
        cor   = AMARELO
    else:
        nivel = "🔴 EVITAR"
        cor   = VERMELHO

    justificativa = " | ".join(fatores) if fatores else "Dados insuficientes para análise detalhada."
    return nivel, score, justificativa, cor


def formatar_numero(valor, moeda=""):
    if valor is None:
        return "N/A"
    if abs(valor) >= 1e12:
        return f"{moeda}{valor/1e12:.2f}T"
    elif abs(valor) >= 1e9:
        return f"{moeda}{valor/1e9:.2f}B"
    elif abs(valor) >= 1e6:
        return f"{moeda}{valor/1e6:.2f}M"
    else:
        return f"{moeda}{valor:,.2f}"


def exibir_painel(ticker_str: str, info: dict, hist, nivel, score, justificativa, cor_rec):
    nome    = info.get("longName") or info.get("shortName") or ticker_str
    preco   = info.get("currentPrice") or info.get("regularMarketPrice", 0)
    moeda   = info.get("currency", "USD")
    simbolo = "R$" if moeda == "BRL" else ("€" if moeda == "EUR" else "$")

    variacao     = info.get("regularMarketChangePercent", 0) or 0
    var_cor      = VERDE if variacao >= 0 else VERMELHO
    var_sinal    = "▲" if variacao >= 0 else "▼"

    mkt_cap      = formatar_numero(info.get("marketCap"), simbolo)
    volume       = formatar_numero(info.get("regularMarketVolume"))
    low52        = info.get("fiftyTwoWeekLow", "N/A")
    high52       = info.get("fiftyTwoWeekHigh", "N/A")
    pe           = info.get("trailingPE") or info.get("forwardPE")
    pe_str       = f"{pe:.2f}" if pe else "N/A"
    dy           = info.get("dividendYield", 0)
    dy_str       = f"{dy*100:.2f}%" if dy else "0.00%"
    setor        = info.get("sector", "N/A")
    industria    = info.get("industry", "N/A")
    pais         = info.get("country", "N/A")
    funcionarios = info.get("fullTimeEmployees")
    func_str     = f"{funcionarios:,}" if funcionarios else "N/A"
    website      = info.get("website", "N/A")

    agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    # ─── CABEÇALHO DA EMPRESA ────────────────────────────────────
    print(f"""
╔═══════════════════════════════════════════════════════════════════════════════════╗
║  {AZUL}{NEGRITO}                                                                  ║
║ {BRANCO}🏢   {nome:<52}{AZUL}                                                     ║
║  {CINZA}Ticker: {BRANCO}{ticker_str:<10}{CINZA}  Setor: {BRANCO}{setor:<30}{AZUL} ║
║  {CINZA}Consultado em: {BRANCO}{agora:<50}{AZUL}                                  ║
╠═══════════════════════════════════════════════════════════════════════════════════╣{RESET}""")

    # ─── PREÇO + VARIAÇÃO ───────────────────────────────────────
    print(f"""{AZUL}{NEGRITO}║  {BRANCO}💰 Preço Atual:  {VERDE}{NEGRITO}{simbolo}{preco:>10.2f} {moeda}   {var_cor}{var_sinal} {variacao:+.2f}%{AZUL}{NEGRITO}                         ║
╠══════════════════════════════════════════════════════════════════════╣{RESET}""")

    # ─── DADOS FUNDAMENTALISTAS ─────────────────────────────────
    dados = [
        ["📊 Market Cap",     mkt_cap,       "📉 Mín 52sem",  f"{simbolo}{low52}"],
        ["📈 Máx 52sem",      f"{simbolo}{high52}", "🔄 Volume",    volume       ],
        ["💹 P/E Ratio",      pe_str,        "💸 Div. Yield",  dy_str       ],
        ["🌍 País",           pais,          "👥 Funcionários", func_str    ],
        ["🏭 Indústria",      industria[:28] if len(industria) > 28 else industria, "🌐 Site", website[:28] if website != "N/A" else website],
    ]

    for row in dados:
        print(f"{AZUL}{NEGRITO}║  {CINZA}{row[0]:<16}{BRANCO}{str(row[1]):<18}{CINZA}{row[2]:<16}{BRANCO}{str(row[3]):<10}{AZUL}{NEGRITO}  ║{RESET}")

    print(f"{AZUL}{NEGRITO}╠══════════════════════════════════════════════════════════════════════╣{RESET}")

    # ─── PLACAR DE RECOMENDAÇÃO ─────────────────────────────────
    barra_cheia   = int(score / 5)   # 0–20 blocos
    barra_vazia   = 20 - barra_cheia
    barra_cor     = VERDE if score >= 70 else (AMARELO if score >= 50 else VERMELHO)
    barra_visual  = f"{barra_cor}{'█' * barra_cheia}{CINZA}{'░' * barra_vazia}{RESET}"

    print(f"""{AZUL}{NEGRITO}║  {BRANCO}🎯 RECOMENDAÇÃO:  {cor_rec}{NEGRITO}{nivel}   {BRANCO}Score: {barra_cor}{score:.0f}/100{AZUL}{NEGRITO}                    ║
║  {RESET}{barra_visual}{AZUL}{NEGRITO}                                       ║
╠══════════════════════════════════════════════════════════════════════╣{RESET}""")

    # ─── JUSTIFICATIVA ──────────────────────────────────────────
    print(f"{AZUL}{NEGRITO}║  {AMARELO}📋 Fatores Analisados:{RESET}")
    for fator in justificativa.split(" | "):
        cor_f = VERDE if "✓" in fator else (VERMELHO if "✗" in fator else CINZA)
        fator_fmt = fator[:68]
        print(f"{AZUL}{NEGRITO}║   {cor_f}• {fator_fmt:<67}{AZUL}{NEGRITO}                            ║{RESET}")

    # ─── DESCRIÇÃO ──────────────────────────────────────────────
    descricao = info.get("longBusinessSummary", "")
    if descricao:
        print(f"{AZUL}{NEGRITO}╠══════════════════════════════════════════════════════════════════════╣")
        print(f"║  {AMARELO}📝 Sobre a Empresa:{RESET}")
        palavras = descricao.split()
        linha = "   "
        for p in palavras[:80]:   # limitar resumo
            if len(linha) + len(p) + 1 > 70:
                print(f"{AZUL}{NEGRITO}║{CINZA} {linha:<69}{AZUL}{NEGRITO}║{RESET}")
                linha = "   " + p + " "
            else:
                linha += p + " "
        if linha.strip():
            print(f"{AZUL}{NEGRITO}║{CINZA} {linha:<69}{AZUL}{NEGRITO}                            ║{RESET}")

    print(f"{AZUL}{NEGRITO}╚══════════════════════════════════════════════════════════════════════╝{RESET}")

    # ─── AVISO LEGAL ────────────────────────────────────────────
    print(f"\n{CINZA}⚠️  Este programa é apenas Acadêmico. Não é aconselhamento financeiro profissional.")
    print(f"   Consulte um especialista antes de investir.{RESET}\n")


def consultar_empresa(entrada: str):
    loading_bar(f"Buscando '{entrada}'")

    ticker_str = buscar_ticker(entrada)

    try:
        ticker = yf.Ticker(ticker_str)
        info   = ticker.info
        hist   = ticker.history(period="3mo")

        if not info or not (info.get("currentPrice") or info.get("regularMarketPrice")):
            # Tenta com .SA para bolsa brasileira
            if not ticker_str.endswith(".SA"):
                ticker_str_sa = ticker_str + ".SA"
                ticker        = yf.Ticker(ticker_str_sa)
                info          = ticker.info
                hist          = ticker.history(period="3mo")
                ticker_str    = ticker_str_sa

            if not info or not (info.get("currentPrice") or info.get("regularMarketPrice")):
                print(f"\n{VERMELHO}❌ Empresa '{entrada}' não encontrada.")
                print(f"{AMARELO}💡 Dica: tente o código da ação diretamente (ex: AAPL, PETR4.SA){RESET}\n")
                return

        nivel, score, justificativa, cor_rec = calcular_recomendacao(info, hist)
        exibir_painel(ticker_str, info, hist, nivel, score, justificativa, cor_rec)

    except Exception as e:
        print(f"\n{VERMELHO}❌ Erro ao consultar: {e}{RESET}\n")


def menu_principal():
    limpar_tela()
    banner()

    historico = []

    while True:
        print(f"{AZUL}{'─'*70}{RESET}")
        print(f"{BRANCO}  Digite o nome ou código da empresa  {CINZA}(ex: Apple, AAPL, Petrobras, PETR4){RESET}")
        print(f"  {CINZA}Comandos: {BRANCO}[H]{CINZA}istórico  {BRANCO}[L]{CINZA}impar  {BRANCO}[S]{CINZA}air{RESET}")
        print(f"{AZUL}{'─'*70}{RESET}")

        try:
            entrada = input(f"\n{AZUL}{NEGRITO}  🔍 Empresa: {RESET}").strip()
        except (KeyboardInterrupt, EOFError):
            print(f"\n\n{AZUL}Até logo! 👋{RESET}\n")
            break

        if not entrada:
            continue

        if entrada.upper() == "S":
            print(f"\n{AZUL}Até logo! 👋{RESET}\n")
            break

        elif entrada.upper() == "L":
            limpar_tela()
            banner()

        elif entrada.upper() == "H":
            if historico:
                print(f"\n{AZUL}{NEGRITO}  📚 Histórico de consultas:{RESET}")
                for i, h in enumerate(historico, 1):
                    print(f"  {CINZA}{i}. {BRANCO}{h}{RESET}")
            else:
                print(f"\n{CINZA}  Nenhuma consulta realizada ainda.{RESET}")
            print()

        else:
            historico.append(entrada)
            consultar_empresa(entrada)

            try:
                continuar = input(f"\n{AZUL}  Pressione Enter para nova consulta ou {BRANCO}[S]{AZUL} para sair: {RESET}").strip()
                if continuar.upper() == "S":
                    print(f"\n{AZUL}Até logo! 👋{RESET}\n")
                    break
            except (KeyboardInterrupt, EOFError):
                print(f"\n\n{AZUL}Até logo! 👋{RESET}\n")
                break


if __name__ == "__main__":
    menu_principal()