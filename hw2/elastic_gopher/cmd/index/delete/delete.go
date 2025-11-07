package delete

import (
	"elastic_gopher/config"
	"elastic_gopher/es"
	"fmt"

	"github.com/spf13/cobra"
)

var SubCmd = &cobra.Command{
	Use:   "delete",
	Short: "Delete an index",
	Long:  "Delete an existing index in elasticsearch specifying its name",
	Args:  cobra.MinimumNArgs(1),
	Run: func(cmd *cobra.Command, args []string) {
		indexName := args[0]
		err := es.DeleteIndex(config.LoadConfig(), indexName)
		if err != nil {
			fmt.Printf("Error while deleting index: %s\n", err)
			return
		}
		fmt.Printf("Deleted index: %s\n", indexName)
	},
}

func Bind(rootCmd *cobra.Command) {
	rootCmd.AddCommand(SubCmd)
}
