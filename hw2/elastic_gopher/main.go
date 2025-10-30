package main

import (
	"elastic_gopher/cmd"
	"elastic_gopher/config"
	"elastic_gopher/es"
	"encoding/json"
	"fmt"
	"time"
)

func test() {
	var configuration = config.LoadConfig()

	//let's create an index
	indexName := "wiki-index"
	mapping := "{\"mappings\":{\"properties\":{\"title\":{\"type\":\"text\"}}}}}"
	document := struct {
		Title string `json:"title"`
	}{
		"Hello World",
	}
	var query = "{\"query\":{\"match_all\":{}}}"

	err := es.CreateIndex(configuration, indexName, mapping)
	if err != nil {
		fmt.Printf("Error creating index: %s\n", err)
	} else {
		fmt.Println("Index created successfully")
	}
	//let's index a document

	data, _ := json.Marshal(document)
	dataStr := string(data)
	err = es.IndexDocument(configuration, indexName, dataStr)
	if err != nil {
		fmt.Println("Error indexing document: ", err)
	} else {
		fmt.Println("Document indexed successfully")
	}

	fmt.Println("Waiting 1 second for document to be indexed...")
	time.Sleep(1 * time.Second) //Wait 1 second for the document to be indexed
	queryResult, err := es.SearchDocument(configuration, indexName, query)

	if err != nil {
		fmt.Println("Error searching document: ", err)
	} else {
		fmt.Println("Search result: ", queryResult)
	}

	//let's delete the index
	err = es.DeleteIndex(configuration, "wiki-index")
	if err != nil {
		fmt.Println("Error deleting index: ", err)
	} else {
		fmt.Println("Index deleted successfully")
	}
}

func main() {
	//test()
	cmd.Execute()

}
