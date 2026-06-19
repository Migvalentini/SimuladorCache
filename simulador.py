import math
import random

def salvar_estado_cache(cache, nome_arquivo):
    with open(nome_arquivo, "w", encoding="utf-8") as f:
        f.write("=== VISUALIZAÇÃO DA MEMÓRIA CACHE ===\n")
        f.write(f"Total de Conjuntos: {len(cache)}\n")
        f.write(f"Linhas por Conjunto (Vias): {len(cache[0])}\n")
        f.write("-" * 50 + "\n\n")
        
        for i_conjunto, conjunto in enumerate(cache):
            f.write(f"Conjunto {i_conjunto:04d}:\n")
            
            for i_linha, linha in enumerate(conjunto):                
                if linha["rotulo"] is not None:
                    rotulo_str = f"0x{linha['rotulo']:04X} ({linha['rotulo']})"
                else:
                    rotulo_str = "--------"
                
                f.write(f"  [Via {i_linha}] Rótulo: {rotulo_str:<12} | Dirty: {linha['dirty']} | LRU: {linha['lru']}\n")
            
            f.write("  " + "-" * 45 + "\n")

teste = False
if teste:
    simulacoes = "simulacoes/teste.txt"
else:
    simulacoes = "simulacoes/oficial.txt"

entradas = [    
"0 8 1024 2 4 LRU 60",
"0 16 512 2 4 LRU 60",
"0 32 256 2 4 LRU 60",
"0 64 128 2 4 LRU 60",
"0 128 64 2 4 LRU 60",
"0 256 32 2 4 LRU 60",
"0 512 16 2 4 LRU 60",
"0 1024 8 2 4 LRU 60",
"0 2048 4 2 4 LRU 60",
"0 4096 2 2 4 LRU 60",
]

def main(entrada):
    valores = entrada.split()
    
    politicaescrita = int(valores[0])
    tamanholinha = int(valores[1])
    numerolinhas = int(valores[2])
    associatividade = int(valores[3])
    tempoacesso = int(valores[4]) # fixo para todas as simulações
    politicasubstituicao = valores[5]
    tempomemoria = int(valores[6]) # fixo para todas as simulações

    enderecocache = 32 # Número fixo pelo enunciado
    numero_conjuntos = int(numerolinhas / associatividade)
    palavra = int(math.log2(tamanholinha)) # Número de bits para a palavra
    conjunto = int(math.log2(numero_conjuntos)) # Número de bits para o conjunto
    rotulo = int(enderecocache - palavra - conjunto) # Número de bits para o rótulo

    cache = []

    # Inicialização da cache
    for c in range(numero_conjuntos):
        conjunto_atual = []
        for l in range(associatividade):
            linha = {
                "rotulo": None,
                "dirty": 0,
                "lru": 0
            }
            conjunto_atual.append(linha)
        cache.append(conjunto_atual)

    # Variáveis para estatísticas
    leiturasMP = 0
    escritasMP = 0
    hitLeitura = 0
    hitEscrita = 0
    escritas = 0
    leituras = 0
    i = 0

    # Processamento do arquivo de simulações
    with open(simulacoes) as f:
        for x in f:
            i += 1
            
            endereco = x.split()[0]
            operacao = x.split()[1]
            
            tamanho = len(endereco) * 4
            binario = f"{int(endereco, 16):b}".zfill(tamanho)
            
            if conjunto == 0:
                enderecorotulo = binario[:-palavra]
                enderecoconjunto = ""
                enderecopalavra = binario[-palavra:]

                rotulo_int = int(enderecorotulo, 2)
                conjunto_int = 0
                palavra_int = int(enderecopalavra, 2)
            else:
                enderecorotulo = binario[:-(palavra + conjunto)]
                enderecoconjunto = binario[-(palavra + conjunto):-palavra]
                enderecopalavra = binario[-palavra:]

                rotulo_int = int(enderecorotulo, 2)
                conjunto_int = int(enderecoconjunto, 2)
                palavra_int = int(enderecopalavra, 2)
            
            conjunto_alvo = cache[conjunto_int] 
            hit = False
            
            for linha in conjunto_alvo:
                if linha["rotulo"] == rotulo_int:
                    hit = True
                    linha_atingida = linha
                    break
                
            if operacao == "W":
                escritas += 1
            else:
                leituras += 1

            if hit:
                if teste:
                    print(f"HIT  | O bloco {rotulo_int:08d}  já estava no conjunto {conjunto_int:08d} | Endereço: {endereco} | Operação: {operacao} - Binário: {enderecorotulo}|{enderecoconjunto}|{enderecopalavra} - Rótulo: {enderecorotulo} ({rotulo_int:08d}) - Conjunto: {enderecoconjunto} ({conjunto_int:08d}) - Palavra: {enderecopalavra} ({palavra_int:08d})")
                if politicasubstituicao == "LRU":
                    for l in conjunto_alvo:
                        if l != linha_atingida and l["rotulo"] is not None:
                            l["lru"] += 1
                    linha_atingida["lru"] = 0
                if operacao == "W":
                    hitEscrita += 1
                    if politicaescrita == 1: #'write-back'
                        linha_atingida["dirty"] = 1
                    else: # 'write-through'
                        escritasMP += 1
                else:
                    hitLeitura += 1
            else:
                if teste:
                    print(f"MISS | O bloco {rotulo_int:08d} não estava no conjunto {conjunto_int:08d} | Endereço: {endereco} | Operação: {operacao} - Binário: {enderecorotulo}|{enderecoconjunto}|{enderecopalavra} - Rótulo: {enderecorotulo} ({rotulo_int:08d}) - Conjunto: {enderecoconjunto} ({conjunto_int:08d}) - Palavra: {enderecopalavra} ({palavra_int:08d})")        

                leiturasMP += 1
                
                linha_alvo = None
                for linha in conjunto_alvo:
                    if linha["rotulo"] is None:
                        linha_alvo = linha
                        break
                
                if linha_alvo is None:
                    if politicasubstituicao == "LRU":
                        linha_alvo = max(conjunto_alvo, key=lambda l: l["lru"])
                    else: # Aleatória
                        linha_alvo = random.choice(conjunto_alvo)
                    
                    if politicaescrita == 1 and linha_alvo["dirty"] == 1:
                        escritasMP += 1

                if politicasubstituicao == "LRU":
                    for l in conjunto_alvo:
                        if l != linha_alvo and l["rotulo"] is not None:
                            l["lru"] += 1
                
                linha_alvo["rotulo"] = rotulo_int
                linha_alvo["lru"] = 0
                
                if operacao == "W":
                    if politicaescrita == 0:   # 'write-through'
                        linha_alvo["dirty"] = 0
                        escritasMP += 1
                    elif politicaescrita == 1: # 'write-back'
                        linha_alvo["dirty"] = 1
                else:
                    linha_alvo["dirty"] = 0
            
        if politicaescrita == 1: # 'write-back'
            for conj in cache:
                for linha in conj:
                    if linha["rotulo"] is not None and linha["dirty"] == 1:
                        escritasMP += 1

    #salvar_estado_cache(cache,  "dados/resultado.txt")

    total_hits = hitLeitura + hitEscrita
    taxa_hit_global  = (total_hits / i) if i > 0 else 0.0
    taxa_hit_leitura = (hitLeitura / leituras) if leituras > 0 else 0.0
    taxa_hit_escrita = (hitEscrita / escritas) if escritas > 0 else 0.0
    taxa_miss_global = 1.0 - taxa_hit_global  
    tempo_medio_acesso = tempoacesso + (taxa_miss_global * tempomemoria)

    #print(f"PARÂMETROS DE ENTRADA: Política de escrita: {politicaescrita} = {'write-through' if politicaescrita == 0 else 'write-back'} | Tamanho da linhas: {tamanholinha} | Número de linhas: {numerolinhas} | Associatividade: {associatividade} | Tempo de acesso: {tempoacesso} ns | Política de substituição: {politicasubstituicao} | Tempo de leitura/escrita: {tempomemoria} ns")
    #print(f"CÁLCULOS PARA A CONFIGURAÇÃO DA CACHE: Tamanho do endereço: {enderecocache} bits | Número de conjuntos: {numero_conjuntos} | Número de bits para o rótulo: {rotulo} | Número de bits para o conjunto: {conjunto} | Número de bits para a palavra: {palavra}")
    #print(f"RESULTADOS DA SIMULAÇÃO: Endereços no arquivo de entrada: {i} | Escritas: {escritas} | Leituras: {leituras} | Escritas da MP: {escritasMP} | Leituras da MP: {leiturasMP}")
    #print(f"ESTATÍSTICAS FINAIS: Taxa de acerto global:  {taxa_hit_global * 100:.4f}% ({total_hits}) | Taxa de acerto leitura: {taxa_hit_leitura * 100:.4f}% ({hitLeitura}) | Taxa de acerto escrita: {taxa_hit_escrita * 100:.4f}% ({hitEscrita}) | Tempo médio de acesso:  {tempo_medio_acesso:.4f} ns")
    print(f"{politicaescrita} {tamanholinha} {numerolinhas} {associatividade} {tempoacesso} {politicasubstituicao} {tempomemoria} | Escritas MP: {escritasMP} - Leituras MP: {leiturasMP} | Escritas: {escritas} - Leituras: {leituras} - Total: {i} | Global:  {taxa_hit_global * 100:.4f}% ({total_hits}) - Leitura: {taxa_hit_leitura * 100:.4f}% ({hitLeitura}) - Escrita: {taxa_hit_escrita * 100:.4f}% ({hitEscrita}) | Acesso:  {tempo_medio_acesso:.4f} ns")
    #print("-" * 100)

for i in range(len(entradas)):
    main(entradas[i])
