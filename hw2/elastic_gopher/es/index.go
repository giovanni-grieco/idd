package es

import (
	"context"
	"elastic_gopher/config"
	"errors"
	"fmt"
	"io"
	"strings"

	"github.com/elastic/go-elasticsearch/v7"
)

func DeleteIndex(config *config.Config, indexName string) error {
	esCfg := elasticsearch.Config{
		Addresses: []string{config.ElasticsearchURL},
	}
	client, err := elasticsearch.NewClient(esCfg)
	if err != nil {
		return err
	}

	_, err = client.Indices.Delete([]string{indexName})
	if err != nil {
		return err
	}
	return nil
}

func CreateIndex(config *config.Config, indexName string, mappings string) error {
	if indexName == "" || indexName == " " {
		return errors.New("invalid index")
	}

	esCfg := elasticsearch.Config{
		Addresses: []string{config.ElasticsearchURL},
	}
	client, err := elasticsearch.NewClient(esCfg)
	if err != nil {
		return err
	}

	_, err = client.Indices.Create(
		indexName,
		client.Indices.Create.WithBody(strings.NewReader(mappings)),
	)

	if err != nil {
		return err
	}
	return nil
}

func IndexDocument(config *config.Config, indexName string, document string) error {

	esCfg := elasticsearch.Config{
		Addresses: []string{config.ElasticsearchURL},
	}
	client, err := elasticsearch.NewClient(esCfg)
	if err != nil {
		return err
	}

	_, err = client.Index(
		indexName,
		strings.NewReader(document),
	)

	if err != nil {
		return err
	}

	return nil
}

func ListIndexes(config *config.Config) (string, error) {
	esCfg := elasticsearch.Config{
		Addresses: []string{config.ElasticsearchURL},
	}
	client, err := elasticsearch.NewClient(esCfg)
	if err != nil {
		return "", err
	}
	indices, err := client.Cat.Indices(
		client.Cat.Indices.WithContext(context.Background()),
		client.Cat.Indices.WithPretty(),
		client.Cat.Indices.WithFormat("json"),
	)
	if err != nil {
		return "", err
	}

	data, err := io.ReadAll(indices.Body)

	err = indices.Body.Close()
	if err != nil {
		return "", err
	}

	result := fmt.Sprintf("%s", data)
	return result, nil
}

func indexDocumentBulk(config *config.Config, indexName string, documents []string) error {
	//TODO: implement bulk indexing
	return nil
}
