package lexer

import "testing"

func Test_lookupIdentifier(t *testing.T) {
	tests := []struct {
		identifier string
		want       string
		wantErr    bool
	}{
		{identifier: "NUM", want: IDENTIFIER},
		{identifier: "num", want: NUM},
		{identifier: "str", want: STR},
		{identifier: "", wantErr: true},
	}
	for _, tt := range tests {
		t.Run(tt.identifier, func(t *testing.T) {
			got, err := lookupIdentifier(tt.identifier)
			if (err != nil) != tt.wantErr {
				t.Errorf("lookupIdentifier() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			if got != tt.want {
				t.Errorf("lookupIdentifier() = %v, want %v", got, tt.want)
			}
		})
	}
}
