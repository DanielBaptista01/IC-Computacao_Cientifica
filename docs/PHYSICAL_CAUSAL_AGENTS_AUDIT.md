# Auditoria científico-computacional — expansão físico-causal v2

## Regra de inclusão

Uma família só entra no corpus validado quando existe, no domínio declarado:

fenômeno -> mecanismo -> equação -> parâmetros -> implementação -> teste ->
simulação -> assinatura.

Nomes de canais não são usados como identidade física. Modelos que ainda não
fecham essa cadeia permanecem explicitamente fenomenológicos, não resolvidos ou
fora de escopo.

## Estado final da auditoria de requisitos

| Requisito | Estado | Decisão |
| --- | --- | --- |
| Separar fonte, agente, mecanismo, canal, ruído e métricas | DONE | schema e exporter preservam campos distintos |
| Transformação Causal Latente com contexto físico | DONE | source, mechanism, physical_parameters e provenance |
| Campo magnético/EM externo | DONE | Zeeman coerente + ensemble quasistático |
| Onda EM coerente próxima à ressonância | DONE | Rabi/RWA com Omega efetivo |
| Banho bosônico térmico | DONE | spin-boson finito |
| Reservatório fotônico T=0 | DONE | relaxação Markoviana |
| Reservatório fotônico a T>0 | DONE | generalized amplitude damping derivado da equação térmica |
| Vibração/fônon por troca de excitação | DONE | modo acústico quantizado + unitária global + traço parcial |
| Vibração/fônon longitudinal | DONE | modo bosônico único, dephasing e recorrência |
| Ruído de carga/TLS | DONE | flutuador biestável RTN + PSD |
| Radiação ionizante/quasipartículas | DONE/PARTIAL | dinâmica pós-impacto quantificada; ponte deposição -> x_qp(0) permanece fenomenológica |
| Reversibilidade por condição | DONE | unitária direta, inversa linear/CPTP e singularidade reduzida distinguidas |
| Tríade Agente–Ruído–Entropia | DONE | métricas e controles coerentes preservam DeltaS=0 com perturbação |
| Identificabilidade por estado | DONE | overlap de variedades parâmetro-tempo |
| Identificabilidade de processo | DONE | embedding multi-probe operacional; não é diamond norm |
| Não-identificabilidade controlada | DONE | duas causas físicas podem compartilhar o mesmo canal de dephasing em um snapshot |
| Dataset separado de labels e pronto para pesquisa posterior | DONE | scientific/features/labels separados, sem ML |
| Main paralela reconciliada | DONE | uma teoria/pipeline autoritativos; caminhos paralelos são facades |
| Hardware/validação experimental | BLOCKED | não há dados experimentais nesta IC |
| Transporte microscópico completo de radiação | BLOCKED | fundamento/escopo insuficientes para uma transformação quantitativa geral |
| Vibração arbitrária de chassi/pacote | BLOCKED | requer plataforma e função de transferência mecânica |
| Ensemble universal 1/f de defeitos | BLOCKED | um RTN físico foi validado; extrapolação universal não é assumida |
| E0/polarização -> Omega universal | BLOCKED | requer matriz de dipolo e geometria específicas da plataforma |

## Oito famílias físico-causais não redundantes

O catálogo autoritativo contém mecanismos distintos, não duplicações por nome:

1. external-magnetic-field-wave;
2. external-electromagnetic-rabi-drive;
3. finite-mode-spin-boson-dephasing;
4. thermal-photon-reservoir;
5. mechanical-phonon-mode;
6. single-mode-mechanical-phonon-dephasing;
7. ionizing-radiation-quasiparticle-burst;
8. bistable-charge-fluctuator-rtn.

O markovian-photon-reservoir-decay permanece no v1 como baseline histórico,
mas não é contado novamente no v2: T=0 é tratado como limite da mesma família
thermal-photon-reservoir.

O helper estático de campo magnético incorporado da implementação paralela foi
mantido como API, mas não virou uma décima identidade causal, pois representa o
mesmo mecanismo Zeeman já coberto por external-magnetic-field-wave.

## Identificabilidade

A análise por estado usa distância de traço entre saídas para o mesmo probe e
procura vizinhos entre as variedades parâmetro-tempo de cada fonte.

A análise de processo concatena as respostas de quatro probes linearmente
independentes (0, 1, +, +i). Sua distância é a RMS das distâncias de traço das
quatro saídas. Ela testa distinguibilidade operacional no protocolo escolhido e
não substitui uma distância diamond.

Um experimento dedicado constrói:
- um campo magnético longitudinal quasistático Gaussiano;
- um banho spin-boson térmico finito;

com o mesmo fator de coerência no snapshot selecionado. Assim, os canais
reduzidos coincidem nesse ponto embora a causa física seja diferente. A
trajetória temporal normalizada é analisada separadamente para buscar informação
adicional. Esse caso é preservado como evidência de não-identificabilidade de
snapshot, e não tratado como falha do modelo.

## Reversibilidade

A classificação continua sendo feita por condição (theta,t), nunca como rótulo
absoluto da fonte. Uma mesma família EM possui regiões unitárias diretamente
invertíveis e regiões de ensemble não unitárias. Mapas reduzidos não unitários
podem continuar linearmente invertíveis sem que sua inversa seja CPTP.

## Quantificação térmica e mecânica

T1* e T2* são reportados como primeiros cruzamentos amostrados de 1/e. Eles não
são chamados de constantes de decaimento quando a dinâmica apresenta recorrência
ou não é exponencial.

Para vibração longitudinal, o teste de frequência mantém a mesma razão
dimensionless g/omega e a mesma ocupação térmica em duas linhas espectrais. A
comparação usa o mesmo tempo físico, permitindo testar se frequência distinta
gera assinatura temporal distinta mesmo sob intensidade adimensional
operacionalmente casada.

## Maturidade

LEVEL_3 significa implementação numérica validada no domínio teórico declarado.
Não significa comparação com hardware nem validação experimental. A família de
radiação é LEVEL_3 apenas para a dinâmica fenomenológica pós-impacto a partir de
x_qp(0).

Os níveis superiores continuam reservados para comparação quantitativa com
referência independente/experimento e validação experimental, quando aplicável.

## Regra epistemológica final

O resultado que o corpus pode testar é:

fontes físicas específicas podem ser individualizadas por mecanismo, parâmetros,
dinâmica e assinatura em determinados regimes observacionais.

O projeto **não** conclui que toda fonte possui uma assinatura universalmente
única.
