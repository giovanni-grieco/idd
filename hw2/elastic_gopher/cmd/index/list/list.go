package list

import (
	"elastic_gopher/config"
	"elastic_gopher/es"
	"fmt"

	"github.com/spf13/cobra"
)

var SubCmd = &cobra.Command{
	Use:   "ls",
	Short: "List indexes",
	Long:  "List indexes",
	Run: func(cmd *cobra.Command, args []string) {
		result, err := es.ListIndexes(config.LoadConfig())
		if err != nil {
			fmt.Printf("Error while listing indexes: %s\n", err)
		} else {
			fmt.Println(result)
		}
	},
}

func Bind(rootCmd *cobra.Command) {
	rootCmd.AddCommand(SubCmd)
}
