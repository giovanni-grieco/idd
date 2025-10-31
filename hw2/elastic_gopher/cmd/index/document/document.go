package document

import (
	"elastic_gopher/cmd/utils"
	"elastic_gopher/config"
	"elastic_gopher/es"
	"encoding/json"
	"fmt"

	"github.com/spf13/cobra"
)

// Possiamo passare direttamente il JSON Raw, oppure gestiamo un minimo l'upload di file? Della serie il nome del file sarà title, e il contenuto sarà body?
// E poi una cosa intermedia dove gli facciamo passare i Fields e costruiamo noi il JSON Raw alla fine? --fields title="Hello World",body="Some content"

var Fields string

var SubCmd = &cobra.Command{
	Use:     "document",
	Short:   "Index a document",
	Long:    "Index a document or a bulk of documents",
	Example: `elastic_gopher index document my-index --fields title="Some Title", body="Some Body"`,
	Args:    cobra.MinimumNArgs(1),
	Run: func(cmd *cobra.Command, args []string) {
		fmt.Println("Document command called")
		indexName := args[0]
		fmt.Printf("Index Name: %s\n", indexName)
		fmt.Printf("Fields: %s\n", Fields)
		fieldsMap, err := utils.FlagParser(Fields)
		if err != nil {
			fmt.Printf("Error while indexing document: %s\n ", err)
		}
		jsonData, err := json.MarshalIndent(fieldsMap, "", "  ")
		if err != nil {
			fmt.Printf("Error while indexing document: %s\n ", err)
		}
		//fmt.Println(string(jsonData))
		err = es.IndexDocument(config.LoadConfig(), indexName, string(jsonData))
		if err != nil {
			fmt.Printf("Error while indexing document: %s\n ", err)
		}
		return
	},
}

func Bind(rootCmd *cobra.Command) {
	SubCmd.Flags().StringVar(&Fields, "fields", "", "--fields title=\"Some Title\",body=\"Some Body\"")
	rootCmd.AddCommand(SubCmd)
}
