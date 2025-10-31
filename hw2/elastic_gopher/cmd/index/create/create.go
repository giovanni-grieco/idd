package create

import (
	"elastic_gopher/config"
	"elastic_gopher/es"
	"fmt"

	"github.com/spf13/cobra"
)

var Mappings string

var SubCmd = &cobra.Command{
	Use:   "create",
	Short: "Create an index in Elasticsearch",
	Long:  `Create a new index in Elasticsearch with the specified name and mapping.`,
	Args:  cobra.MinimumNArgs(1),
	Run: func(cmd *cobra.Command, args []string) {
		fmt.Println("Called create subcommand")
		indexName := args[0]
		fmt.Printf("Index Name: %s\n", indexName)
		fmt.Printf("Mappings: %s\n", Mappings)
		var configuration = config.LoadConfig()
		err := es.CreateIndex(configuration, indexName, Mappings)
		if err != nil {
			fmt.Printf("Error creating index: %s\n", err)
			return
		}
		fmt.Println("Index created successfully")
		// Here you would add the logic to create the index using the provided name and mapping.
	},
}

func Bind(rootCmd *cobra.Command) {
	SubCmd.Flags().StringVar(&Mappings, "mappings", "", "JSON string representing the index mappings")
	rootCmd.AddCommand(SubCmd)
}
