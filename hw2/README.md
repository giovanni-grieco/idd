# Elastic Gopher - a CLI tool for Elasticsearch
Giovanni Pio Grieco - 561105

## Introduzione
Elastic Gopher è un tool CLI sviluppato in Go che permette di interagire con un endpoint Elasticsearch tramite console.

Il codice sorgente si trova su [github](https://github.com/giovanni-grieco/idd/tree/main/hw2) e contiene anche la [documentazione di utilizzo](https://github.com/giovanni-grieco/idd/blob/main/hw2/elastic_gopher/README.md) e alcuni script di esempio.


## Architettura e componenti principali
L'architettura è a strati ed è composta da 2 componenti principali.

Il primo componente di "backend" gestisce l'interazione con la libreria di Elasticsearch, definendo le operazioni chiave e facendo e specificando l'interfaccia di utilizzo allo strato superiore.

Il secondo componente rende possibile l'interazione da console, si occupa di fare il parsing dell'input, di invocare le funzioni dello strato inferiore e di restituire i risultati a video.

## Casi d'uso coperti
- Creazione di un indice con mapping personalizzato (JSON).
- Creazione di un indice usando flag semplificati (per mapping minimali).
- Indicizzazione di singolo documento tramite flag
- Indicizzazione bulk di tutti i file plain-text in una directory specificandone il path.
- Cancellazione di un indice.
- Elenco indici disponibili.
- Ricerca testuale sull'indice.

## Utilizzo
Forma generale:
```bash
elastic_gopher [command] [subcommand] [flags]
```
### Comandi di esempio
- ```elastic_gopher index create wikipedia --mappings "$(cat index_mappings.json)"```
- ```elastic_gopher index ls```
- ```elastic_gopher index delete myindex```
- ```elastic_gopher index document myindex --path path/to/directory```
- ```elastic_gopher index document myindex --fields title="Some Title",body="Some Body"```
- ```elastic_gopher search myindex --fields title="Some text"```

(Per i nomi esatti dei flag consultare la CLI con `elastic_gopher --help` o i singoli sottocomandi `elastic_gopher <comando> --help`.)


## Limitazioni e possibili estensioni
- Gestione avanzata degli errori di rete e retry ancora minimale; si può aggiungere backoff esponenziale.
- Indicizzazione e ricerche batch con parallelismo per throughput maggiore.

## Indicizzazione di alcune pagine di wikipedia
Il [dataset](https://www.kaggle.com/datasets/ltcmdrdata/plain-text-wikipedia-202011) utilizzato per gli esperimenti di esecuzione è composto da pagine wikipedia in plain text.

### Fase preliminare
Dopo aver scaricato un dataset di pagine Wikipedia, bisogna convertire il dataset nel formato desiderato. Il dataset è diviso in diversi chunk di circa 40MB, all'interno di esso le pagine wikipedia sono salvati come JSON. Si è preso in considerazione 1 solo chunk da 30K pagine Wikipedia. 

Il processo di conversione consiste quindi nel prendere il campo "title" del JSON e utilizzarlo per creare un nuovo file. All'interno di questo file si inserisce come contenuto il "text" del JSON.

Si utilizza uno script di conversione [plaintext-wikipedia-converter.py](https://github.com/giovanni-grieco/idd/blob/main/hw2/plaintext-wikipedia-converter.py)

### Indicizzazione
Si crea un indice con 
```bash
elastic_gopher index create wikipedia --mappings "$(cat index_mappings.json)"
```
Nel file ```index_mappings.json``` sono contenute le specifiche del nostro indice.

#### Analyzer e filter

Abbiamo la seguente definizione
```json
"settings": {
    "analysis": {
      "analyzer": {
        "english_text": {
          "tokenizer": "standard",
          "filter": [
            "lowercase",
            "asciifolding",
            "english_stop",
            "english_stemmer"
          ]
        }
      },
      "filter": {
        "english_stop": {
          "type": "stop",
          "stopwords": "_english_"
        },
        "english_stemmer": {
          "type": "stemmer",
          "name": "english"
        }
      }
    }
  },
```

Definiamo un ```english_text``` analyzer che utilizza un tokenizzatore ```standard```.
Si applicano vari filtri come ```lowercase```, ```asciifolding```, ```english_stop``` e  ```english_stemmer```.

Lowercase e Asciifolding servono a ridurre tutto e minuscole e a trasformare caratteri speciali accentati in caratteri senza accento.

English stop gestisce le stop words inglesi mentre lo stemmer porta le parole alla loro radice.

Successivamente si definiscono i mappings come segue:
```json
"mappings": {
    "properties": {
      "title": {
        "type": "text",
        "analyzer": "english_text",
        "fields": {
          "raw": {
            "type": "keyword"
          }
        }
      },
      "content": {
        "type": "text",
        "analyzer": "english_text"
      }
    }
  }
```
Si utilizza l'analyzer definito sopra su entrambi i fields, il titolo però differisce dal contenuto sul fatto che il titolo è di tipo ```keyword```

#### Caricamento file
Per caricare i file e indicizzarli si utilizza
```bash
elastic_gopher index document wikipedia --path ./documents
```
E si attende la fine dell'indicizzazione

### Controllo dell'indice
Utilizziamo ```elastic_gopher index ls``` per assicurarci che l'indice esista e che i documenti siano stati indicizzati.

Nell'output troviamo:
```json
{
    "health" : "yellow",
    "status" : "open",
    "index" : "wikipedia",
    "uuid" : "oTqFpq1eRcOE_yfW3TMMdg",
    "pri" : "1",
    "rep" : "1",
    "docs.count" : "28232",
    "docs.deleted" : "0",
    "store.size" : "105.7mb",
    "pri.store.size" : "105.7mb"
  },
```
L'indice esiste e abbiamo 28mila documenti... bene :)

### Ricerca
Lanciamo la ricerca con
```bash
elastic_gopher search wikipedia "$(cat multi_match_query.json)"
```
dove ```multi_match_query.json``` contiene il JSON della query da eseguire. Ripieghiamo sul raw JSON perchè vogliamo fare una query più complessa, ma se volessimo fare una query semplice si può utilizzare la flag ```---fields a_field="Some Text"```

Il file ```multi_match_query.json``` effettua la ricerca su titolo e contenuto dando più peso al punteggio del titolo.
```json
{
  "query": {
    "multi_match": {
      "query": "Computer Science",
      "fields": ["title^2", "content"]
    }
  }
}
```

Le 10 Query di prova sono state eseguite e salvate in file appositi nella cartella [search_results](https://github.com/giovanni-grieco/idd/tree/main/hw2/search_results) con il loro output relativo.

Un esempio di output con query "Artificial Intelligence ethics and regulations" si può trovare [qui](https://github.com/giovanni-grieco/idd/blob/main/hw2/search_results/Artificial_Intelligence_ethics_and_regulations_results.json).

La quantità di pagine indicizzate non è abbastanza per ottenere buoni risultati con ricerche su argomenti arbitrari. A ogni modo, Elasticsearch ci ritorna documenti che sono relativi all'argomento cercato.

## Conclusioni
Elastic Gopher implementa i requisiti richiesti dall'homework: creazione/cancellazione/lista di indici, definizione mapping, indicizzazione di singoli file o directory e ricerca testuale.