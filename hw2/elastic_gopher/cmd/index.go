package cmd

import (
	"fmt"

	"github.com/spf13/cobra"
)

var indexCommand = &cobra.Command{
	Use:   "index",
	Short: "A subcommand regarding indexing",
	Long:  `A subcommand to perform indexing operations in Elasticsearch.`,
	Run: func(cmd *cobra.Command, args []string) {
		fmt.Println("Indexing called")
		fmt.Printf("Index: %s\n", args[0])
		fmt.Printf("Query: %s\n", args[1])
		// Here you would add the logic to perform the search using the provided index and query.
	},
}

func init() {
	rootCmd.AddCommand(indexCommand)
}
