package document

import (
	"elastic_gopher/cmd/utils"
	"elastic_gopher/config"
	"elastic_gopher/es"
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"strings"

	"github.com/spf13/cobra"
)

// Possiamo passare direttamente il JSON Raw, oppure gestiamo un minimo l'upload di file? Della serie il nome del file sarà title, e il contenuto sarà body?
// E poi una cosa intermedia dove gli facciamo passare i Fields e costruiamo noi il JSON Raw alla fine? --fields title="Hello World",body="Some content"

var Fields string
var Path string

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
		if Path != "" {
			fmt.Printf("Path: %s\n", Path)
			handleDocumentIndexingUsingPath(args)
		} else {
			fmt.Printf("Fields: %s\n", Fields)
			handleDocumentIndexingUsingFields(args)
		}

	},
}

func handleDocumentIndexingUsingPath(args []string) {
	indexName := args[0]
	if Path == "" {
		// no path provided, nothing to do
		return
	}

	info, err := os.Stat(Path)
	if err != nil {
		fmt.Printf("Error accessing path %s: %v\n", Path, err)
		return
	}

	if info.IsDir() {
		// walk directory recursively and index files
		err = filepath.Walk(Path, func(p string, fi os.FileInfo, err error) error {
			if err != nil {
				fmt.Printf("Skipping %s: %v\n", p, err)
				return nil
			}
			if fi.IsDir() {
				return nil
			}
			if err := indexFile(indexName, p); err != nil {
				fmt.Printf("Error indexing %s: %v\n", p, err)
			}
			return nil
		})
		if err != nil {
			fmt.Printf("Error walking path %s: %v\n", Path, err)
		}
	} else {
		// single file
		if err := indexFile(indexName, Path); err != nil {
			fmt.Printf("Error indexing %s: %v\n", Path, err)
		}
	}
}

func indexFile(indexName, filePath string) error {
	data, err := os.ReadFile(filePath)
	if err != nil {
		return fmt.Errorf("read file: %w", err)
	}

	title := strings.TrimSuffix(filepath.Base(filePath), filepath.Ext(filePath))
	doc := map[string]string{
		"title":   title,
		"content": string(data),
	}

	jsonData, err := json.MarshalIndent(doc, "", "  ")
	if err != nil {
		return fmt.Errorf("marshal json: %w", err)
	}

	if err := es.IndexDocument(config.LoadConfig(), indexName, string(jsonData)); err != nil {
		return fmt.Errorf("es index: %w", err)
	}

	fmt.Printf("Indexed %s as title=%s into index=%s\n", filePath, title, indexName)
	return nil
}

func handleDocumentIndexingUsingFields(args []string) {
	indexName := args[0]
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
}

func Bind(rootCmd *cobra.Command) {
	SubCmd.Flags().StringVar(&Fields, "fields", "", "--fields title=\"Some Title\",body=\"Some Body\"")
	SubCmd.Flags().StringVar(&Path, "path", "", "--path path/to/file/or/folder")
	rootCmd.AddCommand(SubCmd)
}
