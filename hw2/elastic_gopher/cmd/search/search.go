package search

import (
	"elastic_gopher/config"
	"elastic_gopher/es"
	"encoding/json"
	"fmt"
	"strings"

	"github.com/spf13/cobra"
)

var Fields string

func ParseFieldsToQuery(fields string) string {
	if fields != "" {
		// Parse SearchFields into a map
		kvMap := make(map[string]string)
		pairs := strings.Split(fields, ",")
		for _, pair := range pairs {

			kv := strings.SplitN(pair, "=", 2)
			if len(kv) == 2 {
				kvMap[strings.TrimSpace(kv[0])] = strings.TrimSpace(kv[1])
			}
		}
		// Build a match query
		match := make(map[string]interface{})
		for k, v := range kvMap {
			match[k] = v
		}
		esQuery := map[string]interface{}{
			"query": map[string]interface{}{
				"match": match,
			},
		}
		b, _ := json.Marshal(esQuery)
		return string(b)
	} else {
		return ""
	}
}

var SearchCmd = &cobra.Command{
	Use:     "search",
	Short:   "Search in the specified index",
	Long:    `Search for documents in the specified Elasticsearch index using a provided query.`,
	Args:    cobra.MinimumNArgs(1),
	Example: `elastic_gopher search my-index '{"query":{"match_all":{}}}' OR elastic_gopher search my-index --fields title="Some Title",body="Some Body"`,
	Run: func(cmd *cobra.Command, args []string) {
		var query string
		query = ParseFieldsToQuery(Fields)
		if query != "" {
			fmt.Printf("Built query from SearchFields: %s\n", query)
		} else {
			query = args[1]
			fmt.Printf("Query: %s\n", query)
		}

		var configuration = config.LoadConfig()
		result, err := es.SearchDocument(configuration, args[0], query)
		if err != nil {
			fmt.Printf("error searching document: %s\n", err)
			return
		}
		fmt.Println(result)
		// Optionally: unmarshal and pretty-print result
	},
}

func Bind(rootCmd *cobra.Command) {
	SearchCmd.Flags().StringVar(&Fields, "fields", "", "Key-value pairs to build a match query (e.g. title=\"Some Title\",body=\"Some Body\")")
	rootCmd.AddCommand(SearchCmd)
}
