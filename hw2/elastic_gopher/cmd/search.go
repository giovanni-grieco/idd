package cmd

import (
	"fmt"
	"github.com/spf13/cobra"
)

var searchCmd = &cobra.Command{
	Use:   "search",
	Short: "Search in the specified index",
	Long:  `Search for documents in the specified Elasticsearch index using a provided query.`,
	Run: func(cmd *cobra.Command, args []string) {
		fmt.Println("search called")
		fmt.Printf("Index: %s\n", args[0])
		fmt.Printf("Query: %s\n", args[1])
		// Here you would add the logic to perform the search using the provided index and query.
	},
}

func init() {
	rootCmd.AddCommand(searchCmd)
}
