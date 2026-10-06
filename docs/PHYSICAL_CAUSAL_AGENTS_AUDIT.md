# Auditoria científico-computacional — expansão físico-causal v2

## Escopo

A versão ic_causal_agents_final_v1 permanece congelada como baseline
mecanístico. Esta auditoria avalia quais fontes físicas originalmente motivadoras
da IC podem ser promovidas a famílias causalmente modeladas sem reduzir a fonte ao
nome de um canal.

Critério de inclusão:

fenômeno físico -> mecanismo -> equação -> parâmetros -> implementação -> teste
-> simulação -> assinatura.

## Estado auditado

| Fonte candidata | Situação antes do v2 | Decisão |
| --- | --- | --- |
| Campo/onda eletromagnética externa | somente reservatório fotônico e detuning abstrato | implementar componente magnética semiclassica + regime quasistático |
| Reservatório térmico | spin-boson finito já validado | reutilizar como fonte térmica explícita, preservando unidades naturais |
| Vibração mecânica/fônons | não havia família mecânica explícita | implementar modo acústico quantizado + traço parcial |
| Radiação cósmica/ionizante | ausente | implementar apenas ponte pós-impacto via quasipartículas; não inventar Hamiltoniano da partícula |
| Campo magnético | parcialmente implícito em detuning | tornar fonte/orientação/amplitude/frequência explícitas |
| Ruído de carga/TLS | ausente | implementar flutuador biestável com random telegraph noise exato |
| Reservatório eletromagnético de fótons | já validado | preservar como fonte física radiativa |
| Quasipartículas | ausentes como estado causal intermediário | quantificar cinética pós-impacto no modelo de radiação |

## Decisões epistemológicas

### Campo eletromagnético

O v2 modela a componente magnética de um campo externo em um qubit spin-1/2
efetivo por acoplamento Zeeman. O regime determinístico é unitário. O regime
quasistático Gaussiano é uma média de ensemble e gera dephasing. Assim, a mesma
categoria de fonte física pode possuir classes de reversibilidade diferentes.

A família não representa automaticamente toda interferência eletromagnética e não
substitui uma futura implementação de acoplamento elétrico de dipolo.

### Térmico

O spin-boson finito é reclassificado semanticamente como fonte física de banho
bosônico térmico, sem alterar sua matemática. A temperatura do modelo original é
uma escala energética/frequencial em unidades naturais; não é convertida
silenciosamente em kelvin de um dispositivo específico.

### Mecânico

O modelo usa um modo mecânico/acústico quantizado e interação
Jaynes-Cummings. A dinâmica reduzida é derivada de uma unitária global e de um
estado térmico do modo. O espaço de Fock é truncado numericamente e a dimensão da
truncatura é registrada como metadata.

### Radiação ionizante

A cadeia física é preservada como:

evento ionizante -> deposição de energia -> fônons de alta energia ->
quasipartículas -> aumento de Gamma_1 -> relaxação do qubit.

A simulação começa em x_qp(0). A conversão de energia/localização/multiplicidade
do evento para x_qp(0) permanece não resolvida. Por isso o registro possui
proveniência PHENOMENOLOGICAL no elo fonte->canal e não declara um Hamiltoniano
microscópico fictício.

### Carga/defeito biestável

A fonte é um defeito/armadilha de carga com dois estados. Seu efeito é uma
modulação longitudinal telegráfica da frequência do qubit. O canal de dephasing é
consequência da média sobre o processo, não a identidade do agente.

## Análise de identificabilidade

As seis fontes usam escalas temporais diferentes. Comparar numericamente tempos
iguais de um campo EM e de um banho em unidades naturais não possui significado
causal geral. O v2 adota análise de sobreposição de assinaturas por estado de prova,
calculando distância de traço ao vizinho mais próximo entre as variedades
paramétrico-temporais de cada fonte.

O valor em t=0 é mantido como colisão física real. O relatório inclui também o
mínimo excluindo t=0.

Para mecanismos de dephasing são comparadas separadamente formas temporais
representativas de campo quasistático Gaussiano, spin-boson térmico e RTN de carga.

## Maturidade

As seis famílias do catálogo v2 são LEVEL_3 quanto à implementação numérica.
Isso não significa validação experimental. Em particular, o modelo de radiação é
LEVEL_3 para a dinâmica fenomenológica pós-impacto, não para transporte de
partículas ou predição de x_qp(0) a partir de energia depositada.
