package es

import (
	"bytes"
	"context"
	"elastic_gopher/config"
	"encoding/json"
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

func IndexDocumentBulk(config *config.Config, indexName string, documents []string) error {
	if len(documents) == 0 {
		return nil
	}

	esCfg := elasticsearch.Config{
		Addresses: []string{config.ElasticsearchURL},
	}
	client, err := elasticsearch.NewClient(esCfg)
	if err != nil {
		return err
	}

	const batchSize = 500

	for i := 0; i < len(documents); i += batchSize {
		end := i + batchSize
		if end > len(documents) {
			end = len(documents)
		}

		var buf bytes.Buffer
		for _, doc := range documents[i:end] {
			// action/meta line
			meta := map[string]map[string]string{"index": {"_index": indexName}}
			metaLine, _ := json.Marshal(meta)
			buf.Write(metaLine)
			buf.WriteByte('\n')
			// document line
			buf.WriteString(doc)
			buf.WriteByte('\n')
		}

		res, err := client.Bulk(bytes.NewReader(buf.Bytes()), client.Bulk.WithContext(context.Background()))
		if err != nil {
			return err
		}
		body, err := io.ReadAll(res.Body)
		_ = res.Body.Close()
		if err != nil {
			return err
		}

		if res.IsError() {
			return fmt.Errorf("bulk request failed: %s", string(body))
		}

		var resp map[string]interface{}
		if err := json.Unmarshal(body, &resp); err != nil {
			return fmt.Errorf("failed to parse bulk response: %w", err)
		}

		if hasErrors, _ := resp["errors"].(bool); hasErrors {
			// collect item errors
			items, _ := resp["items"].([]interface{})
			var sb strings.Builder
			for _, it := range items {
				itMap, _ := it.(map[string]interface{})
				for _, v := range itMap {
					vMap, _ := v.(map[string]interface{})
					if errInfo, ok := vMap["error"]; ok {
						errBytes, _ := json.Marshal(errInfo)
						sb.Write(errBytes)
						sb.WriteByte('\n')
					}
				}
			}
			if sb.Len() > 0 {
				return fmt.Errorf("bulk item errors:\n%s", sb.String())
			}
		}
	}

	return nil
}
