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
    # json.dumps transforma a estrutura de dados (listas e dicts) em uma string JSON
    # 'indent=4' organiza o arquivo com recuos, tornando-o humano e legível
    cache_json = json.dumps(cache, indent=4)
    
    with open(nome_arquivo, "w", encoding="utf-8") as f:
        f.write(cache_json)
        
    print(f"Estrutura real da cache exportada com sucesso para '{nome_arquivo}'!")

def salvar_estado_cache(cache, nome_arquivo="visualizacao_cache.txt"):
    with open(nome_arquivo, "w", encoding="utf-8") as f:
        f.write("=== VISUALIZAÇÃO DA MEMÓRIA CACHE ===\n")
        f.write(f"Total de Conjuntos: {len(cache)}\n")
        f.write(f"Linhas por Conjunto (Vias): {len(cache[0])}\n")
        f.write("-" * 50 + "\n\n")
        
        # Varre cada conjunto da cache
        for i_conjunto, conjunto in enumerate(cache):
            f.write(f"Conjunto {i_conjunto:04d}:\n")
            
            # Varre cada linha (via) daquele conjunto
            for i_linha, linha in enumerate(conjunto):
                status = "VÁLIDO" if linha["valido"] else "INVAL"
                
                # Formata o rótulo: se for None mostra '--------', se tiver número mostra em Hex/Decimal
                if linha["rotulo"] is not None:
                    rotulo_str = f"0x{linha['rotulo']:04X} ({linha['rotulo']})"
                else:
                    rotulo_str = "--------"
                
                # Cria a linha de texto bonitinha e alinhada
                f.write(f"  [Via {i_linha}] Status: {status} | Rótulo: {rotulo_str:<12} | Dirty: {linha['dirty']} | LRU: {linha['lru']}\n")
            
            f.write("  " + "-" * 45 + "\n")
            
    print(f"Estado da cache exportado com sucesso para '{nome_arquivo}'!")

print("Digite as configurações da memória cache (política de escrita, tamanho da linha, número de linhas, associatividade, tempo de acesso, política de substituição) e da memória principal (tempo de leitura/escrita):")
input = input().split()
politicaescrita = int(input[0])
tamanholinha = int(input[1])
numerolinhas = int(input[2])
associatividade = int(input[3])
tempoacesso = int(input[4])
politicasubstituicao = input[5]
tempomemoria = int(input[6])

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
    
salvar_estado_cache(cache, "cache_inicial.txt")

cache[0][0] = {"valido": True, "rotulo": 25, "dirty": 1, "lru": 2}
cache[0][1] = {"valido": True, "rotulo": 84, "dirty": 0, "lru": 1}
cache[5][0] = {"valido": True, "rotulo": 1024, "dirty": 0, "lru": 1}

salvar_estado_cache(cache, "cache_com_dados.txt")
salvar_cache_como_json(cache, "cache_real.json")
    
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
    
    print("Endereço: " + str(endereco) + " - Operação: " + operacao + " - Binário: " + binario + " - Rótulo: " + enderecorotulo + " (" + str(rotulo_int) + ")" + " - Conjunto: " + enderecoconjunto + " (" + str(conjunto_int) + ")" + " - Linha: " + enderecolinha + " (" + str(linha_int) + ")")
    
    conjunto_alvo = cache[conjunto_int] 
    hit = False

    # Percorre as vias do conjunto X
    for linha in conjunto_alvo:
        if linha["valido"] == True and linha["rotulo"] == rotulo_int:
            hit = True
            linha_atingida = linha
            break

    if hit:
        print("Sucesso! O bloco 985 já estava no conjunto 270. Temos um HIT.")
        # Aqui você atualiza o LRU e trata se for escrita (W)
    else:
        print("O bloco 985 não está aqui. Temos um MISS.")
        # Aqui você aplica a lógica de carregar o bloco da Memória Principal
    
    if operacao == "W":
        enderecosescrita += 1
    elif operacao == "R":
        enderecosleitura += 1
    
    i += 1

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