# Auditoria de Fechamento Científico

## Escopo

A linha final consolida o conteúdo científico válido dos PRs #1, #2 e #3 e
evolui essa base para quatro famílias, Dataset Final, análise N-agentes,
evidências, gráficos e reprodução em uma etapa.

## Perguntas finais

### Há afirmação não sustentada?

Foram evitadas as interpretações de que canal efetivo identifica a fonte, todo
canal não unitário é simplesmente irreversível, entropia nula implica ausência
de perturbação, toda assinatura é única, recorrência do banho finito representa
universalmente não-Markovianidade ou singularidade numérica equivale
automaticamente a não-invertibilidade matemática.

### Há resultado importante sem teste?

Os pontos usados no fechamento possuem testes automatizados: quatro famílias,
limites nulos, soluções analíticas, Kraus/CPTP, recorrência spin-boson,
equivalência microscópica/reduzida, separação features/labels, strict JSON,
identificabilidade N-agentes e dinâmica unitária com $\Delta S$ numericamente nulo.

### Há número do relatório não reproduzível?

Os números finais são gerados por ic-finalize e escritos em CSV, JSON e
Markdown. O Relatório Final não deve usar valores calculados manualmente.

### Há hipótese autoral apresentada como fato estabelecido?

A documentação mantém separada a formalização autoral Agente Causal dos
formalismos estabelecidos de sistemas abertos. A conclusão é operacional e
condicional, não ontológica.

### Há implementação relevante apenas em branch antiga?

feat/fase2-finalizacao-ic deriva da linha empilhada mais avançada e contém todo
o desenvolvimento válido dos PRs #1–#3. Após sua integração em main, os PRs
anteriores devem ser encerrados como superseded.

## Limite de escopo

A IC termina em modelagem, simulação, coleta, validação, dataset e análise de
identificabilidade/reversibilidade. Machine Learning e QML permanecem fora.
