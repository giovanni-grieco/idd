package create

import (
	"fmt"

	"github.com/spf13/cobra"
)

var Fields string
var Name string

var createSubCmd = &cobra.Command{
	Use:   "create",
	Short: "Create an index in Elasticsearch",
	Long:  `Create a new index in Elasticsearch with the specified name and mapping.`,
	Args:  cobra.MinimumNArgs(0),
	Run: func(cmd *cobra.Command, args []string) {
		fmt.Println("Called create subcommand")
		// Here you would add the logic to create the index using the provided name and mapping.
	},
}

func Bind(rootCmd *cobra.Command) {
	createSubCmd.Flags().StringVar(&Name, "name", "", "Name of the index to perform operations on")
	createSubCmd.Flags().StringVar(&Fields, "fields", "", "Fields to index in key=value format, separated by commas")
	rootCmd.AddCommand(createSubCmd)
}
