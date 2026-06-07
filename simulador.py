#Memória Cache:
# 1 - Política de escrita: 0 - write-through e 1 - write-back;
# 2 - Tamanho da linha: deve ser potência de 2, em bytes;
# 3 - Número de linhas: deve ser potência de 2;
# 4 - Associatividade (número de linhas) por conjunto: deve ser potência de 2 (mínimo 1 e máximo igual ao número de linhas);
# 5 - Tempo de acesso quando encontra (hit time): em nanossegundos;
# 6 - Política de Substituição: LRU (Least Recently Used) ou Aleatória;

#Memória Principal:
# 7 - Tempos de leitura/escrita: em nanossegundos.


# 0 64 4096 2 10 LRU 80

import math
import json

def salvar_cache_como_json(cache, nome_arquivo="cache_real.json"):
    cache_json = json.dumps(cache, indent=4)
    
    with open(nome_arquivo, "w", encoding="utf-8") as f:
        f.write(cache_json)

def salvar_estado_cache(cache, nome_arquivo="visualizacao_cache.txt"):
    with open(nome_arquivo, "w", encoding="utf-8") as f:
        f.write("=== VISUALIZAÇÃO DA MEMÓRIA CACHE ===\n")
        f.write(f"Total de Conjuntos: {len(cache)}\n")
        f.write(f"Linhas por Conjunto (Vias): {len(cache[0])}\n")
        f.write("-" * 50 + "\n\n")
        
        for i_conjunto, conjunto in enumerate(cache):
            f.write(f"Conjunto {i_conjunto:04d}:\n")
            
            for i_linha, linha in enumerate(conjunto):
                status = "VÁLIDO" if linha["valido"] else "INVAL"
                
                if linha["rotulo"] is not None:
                    rotulo_str = f"0x{linha['rotulo']:04X} ({linha['rotulo']})"
                else:
                    rotulo_str = "--------"
                
                f.write(f"  [Via {i_linha}] Status: {status} | Rótulo: {rotulo_str:<12} | Dirty: {linha['dirty']} | LRU: {linha['lru']}\n")
            
            f.write("  " + "-" * 45 + "\n")

politicaescrita = 0
tamanholinha = 64
numerolinhas = 4096
associatividade = 2
tempoacesso = 10
politicasubstituicao = "LRU"
tempomemoria = 80

enderecocache = 32 # Número fixo pelo enunciado
numero_conjuntos = int(numerolinhas / associatividade)
palavra = int(math.log2(tamanholinha)) # Número de bits para a palavra
conjunto = int(math.log2(numero_conjuntos)) # Número de bits para o conjunto
rotulo = int(enderecocache - palavra - conjunto) # Número de bits para o rótulo

print(f"Configurações da memória cache e memória principal:")
print(f"Política de escrita: {politicaescrita}")
print(f"Tamanho da linhas: {tamanholinha}")
print(f"Número de linhas: {numerolinhas}")
print(f"Associatividade: {associatividade}")
print(f"Tempo de acesso: {tempoacesso} ns")
print(f"Política de substituição: {politicasubstituicao}")
print(f"Tempo de leitura/escrita: {tempomemoria} ns")
print(f"Tamanho do endereço: {enderecocache} bits")
print(f"Número de conjuntos: {numero_conjuntos}")
print(f"\nNúmero de bits para o rótulo: {rotulo}" + f"\nNúmero de bits para o conjunto: {conjunto}" + f"\nNúmero de bits para a palavra: {palavra}")

cache = []

for c in range(numero_conjuntos):
    conjunto_atual = []
    for l in range(associatividade):
        linha = {
            "valido": False,
            "rotulo": None,
            "dirty": 0,
            "lru": 0
        }
        conjunto_atual.append(linha)
    cache.append(conjunto_atual)
    
salvar_estado_cache(cache, "cache.txt")
salvar_cache_como_json(cache, "cache.json")
    
enderecosescrita = 0
enderecosleitura = 0
i = 0
with open("teste.txt") as f:
  for x in f:
    endereco = x.split()[0]
    operacao = x.split()[1]
    
    tamanho = len(endereco) * 4
    binario = f"{int(endereco, 16):b}".zfill(tamanho)
    
    enderecorotulo = binario[:-(palavra + conjunto)]
    enderecoconjunto = binario[-(palavra + conjunto):-palavra]
    enderecolinha = binario[-palavra:]
    
    rotulo_int = int(enderecorotulo, 2)
    conjunto_int = int(enderecoconjunto, 2)
    linha_int = int(enderecolinha, 2)
    
    print("Endereço: " + str(endereco) + 
          " - Operação: " + operacao + 
          " - Binário: " + binario + 
          " - Rótulo: " + enderecorotulo + " (" + str(rotulo_int) + ")" + 
          " - Conjunto: " + enderecoconjunto + " (" + str(conjunto_int) + ")" + 
          " - Linha: " + enderecolinha + " (" + str(linha_int) + ")")
    
    conjunto_alvo = cache[conjunto_int] 
    hit = False
    
    for linha in conjunto_alvo:
        print(linha)
        if linha["valido"] == True and linha["rotulo"] == rotulo_int:
            hit = True
            linha_atingida = linha
            break

    if hit:
        print(f"Sucesso! O bloco {rotulo_int} já estava no conjunto {conjunto_int}. Temos um HIT.")
        if politicasubstituicao == "LRU":
            for l in conjunto_alvo:
                if l["lru"] < linha_atingida["lru"]:
                    l["lru"] += 1
            linha_atingida["lru"] = 0
        if operacao == "W":
            enderecosescrita += 1
            if politicaescrita == 1:
                linha_atingida["dirty"] = 1
        else:
            enderecosleitura += 1
    else:
        print(f"O bloco {rotulo_int} não está aqui. Temos um MISS.")
        if operacao == "W":
            enderecosescrita += 1
        else:
            enderecosleitura += 1
    
    i += 1
    
    break

#ts = ℎ × 𝑡1 + (1 − ℎ) × (𝑡1 + 𝑡2)
#   = 𝑡1 + (1 − ℎ) × 𝑡2

#onde
#h = taxa de acerto
#t1 = tempo de acesso da M1 (cache, cache de disco,..)
#t2 = tempo de acesso de M2 (memória principal, disco)


print("Parâmetros de entrada:")
print("Política de escrita: " + ("write-through" if politicaescrita == 0 else "write-back"))
print("Tamanho da linha: " + str(tamanholinha) + " bytes")
print("Número de linhas: " + str(numerolinhas))
print("Associatividade (número de linhas) por conjunto: " + str(associatividade))
print("Tempo de acesso quando encontra (hit time): " + str(tempoacesso) + " ns")
print("Política de Substituição: " + politicasubstituicao)

print("Total de endereços no arquivo de entrada: " + str(i))
print("Total de escritas: " + str(enderecosescrita))
print("Total de leituras: " + str(enderecosleitura))
print("Total de escritas e leituras da memória principal: " + str(enderecosescrita + enderecosleitura))

print("Taxa de acerto (hit rate): especificar esta taxa por leitura, escrita e global (colocar ao lado a quantidade);")
#ainda falta fazer a simulação para calcular a taxa de acerto

print("Tempo médio de acesso da cache (em ns): utilizar a fórmula vista em aula;")
#ainda falta fazer a simulação para calcular o tempo médio de acesso