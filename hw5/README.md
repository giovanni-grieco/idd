# Homework 5
Estrazione ed indicizzazione di paper provenienti da Arxiv e PubMed

## Argomenti
- Arxiv: "text-to-sql" or "Natural language to sql"
- PubMed: "glyphosate AND cancer risk"

## Step
- Indicizzazione dei documenti. Scrivere il codice per indicizzare gli articoli utilizzando Elasticsearch (o Lucene), includendo i seguenti campi: titolo, autori, data, abstract, testo completo. 
- Funzionalità di ricerca base. Il sistema deve permettere interrogazioni su uno o più campi, ricerca per parole chiave, combinazioni di query (es. ricerca booleana, full-text). Le funzionalità di ricerca devono essere disponibili tramite una semplice shell su riga di comando e tramite una semplice interfaccia web. 
- Estrazione delle tabelle. Scrivere il codice per estrarre dagli articoli del corpus tutte le tabelle con associati dati di contesto. In particolare, per ogni tabella, estrare il corpo, la caption, i paragrafi che la citano, i paragrafi che contengono termini presenti nella tabella o nella caption (evitando di considerare termini non informativi).
- Estrazione delle figure. Scrivere il codice per estrarre dagli articoli del corpus tutte le figure con associati dati di contesto. In particolare, per ogni figura, estrare l'url, la caption, i paragrafi che la citano, i paragrafi che citano termini presenti nella caption (evitando di considerare termini non informativi).
- Indicizzazione delle tabelle. Scrivere il codice per indicizzare le tabelle utilizzando Elasticsearch (o Lucene). Ogni tabella viene indicizzata come un documento, con i seguenti campi: paper_id (ID dell'articolo), table_id (ID della tabella all’interno dell’articolo),  caption (testo della caption della tabella), body (contenuto della tabella come testo), mentions (lista dei paragrafi del paper che citano la tabella), context_paragraphs (lista dei paragrafi del paper che contengono termini presenti nella tabella o nella caption).
- Indicizzazione delle figure. Scrivere il codice per indicizzare le figure utilizzando Elasticsearch (o Lucene). Ogni figura viene indicizzata come un documento, con i seguenti campi: url (url della figura), paper_id (ID dell'articolo), table_id (ID della figura all’interno dell’articolo),  caption (testo della caption della figura), mentions (lista dei paragrafi del paper che citano la figura).
- Funzionalità di ricerca avanzate. Il sistema deve permettere interrogazioni per tabelle, figure, documenti su uno o più campi, ricerca per parole chiave, combinazioni di query (es. ricerca booleana, full-text). Le funzionalità di ricerca devono essere disponibili tramite una semplice shell su riga di comando e tramite una semplice interfaccia web. 

## Documentazione
Per arxiv [qui](https://info.arxiv.org/help/api/user-manual.html) dovrebbe esserci la maggiorparte della roba

# Client & Indexer

Sono disponibili due sistemi principale, il primo è un client che permette di interagire con elastic search tramite una GUI, mentre il secondo sistema è quello che si occupa di scaricare i dati, elaborarli secondo le specifiche e indicizzarli all'interno di elastic search.