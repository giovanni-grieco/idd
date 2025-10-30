package es

import (
	"elastic_gopher/config"
	"fmt"
	"io"
	"strings"

	"github.com/elastic/go-elasticsearch/v7"
)

func SearchDocument(config *config.Config, indexName string, query string) (string, error) {
	esCfg := elasticsearch.Config{
		Addresses: []string{config.ElasticsearchURL},
	}
	client, err := elasticsearch.NewClient(esCfg)
	if err != nil {
		return "", err
	}

	res, err := client.Search(
		client.Search.WithIndex(indexName),
		client.Search.WithBody(strings.NewReader(query)),
	)
	if err != nil {
		return "", err
	}
	data, err := io.ReadAll(res.Body)
	if err != nil {
		return "", err
	}
	err = res.Body.Close()
	if err != nil {
		return "", err
	}
	result := fmt.Sprintf("%s", data)
	return result, nil
}
