# Ci sono tante figure, per ogni figura ci sono potenzialmente più paragrafi che la citano...
# Possiamo quindi estrarre la figura e anche i paragrafi, ma come salviamo queste informazioni?
# Dati semi-strutturati? Un json per le figure di un paper con i relativi riferimenti ai paragrafi? Ma i paragrafi come li salviamo?
# Come stringoni nel json direttamente? E se si, direttamente ripuliti dell'HTML? Forse no. Meglio lasciare
# Però forse non è ottimo salvare i paragrafi come stringhe, forse è meglio salvare gli indici di inizio e fine nel testo originale del paper
# Allora dobbiamo creare un paragraph extractor che ci dia gli indici di inizio e fine di ogni paragrafo nel testo originale

# allora possiamo scomporre il problema in estrazione e linking. Vogliamo estrarre le figure e i paragrafi che le citano
# poi vogliamo linkare le figure ai paragrafi che le citano