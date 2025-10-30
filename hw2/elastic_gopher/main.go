package main

import (
	"encoding/json"
	"fmt"
	"github.com/spf13/cobra"
	"time"
)

func test() {
	var config = LoadConfig()

	//let's create an index
	indexName := "wiki-index"
	mapping := "{\"mappings\":{\"properties\":{\"title\":{\"type\":\"text\"}}}}}"
	document := struct {
		Title string `json:"title"`
	}{
		"Hello World",
	}
	var query = "{\"query\":{\"match_all\":{}}}"

	err := createIndex(config, indexName, mapping)
	if err != nil {
		fmt.Printf("Error creating index: %s\n", err)
	} else {
		fmt.Println("Index created successfully")
	}
	//let's index a document

	data, _ := json.Marshal(document)
	dataStr := string(data)
	err = indexDocument(config, indexName, dataStr)
	if err != nil {
		fmt.Println("Error indexing document: ", err)
	} else {
		fmt.Println("Document indexed successfully")
	}
	time.Sleep(1000 * time.Millisecond)
	queryResult, err := searchDocument(config, indexName, query)

	if err != nil {
		fmt.Println("Error searching document: ", err)
	} else {
		fmt.Println("Search result: ", queryResult)
	}

	//let's delete the index
	err = deleteIndex(config, "wiki-index")
	if err != nil {
		fmt.Println("Error deleting index: ", err)
	} else {
		fmt.Println("Index deleted successfully")
	}
}

func main() {
	test()

	//var config *Config = LoadConfig()

}
