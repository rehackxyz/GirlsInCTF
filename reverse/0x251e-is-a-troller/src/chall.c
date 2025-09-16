#include <stdio.h>
#include <string.h>

int main() {
    char input[100];
    char correct_flag[] = "GCTF25{0x251e_tr0ll_m4st3r}";
    
    printf("=== 0x251e's Simple Crackme ===\n");
    printf("Enter the flag: ");
    
    fgets(input, sizeof(input), stdin);
    input[strcspn(input, "\n")] = 0;  // Remove newline
    
    if(strcmp(input, correct_flag) == 0) {
        printf("Congratulations! You solved it!\n");
        printf("Flag: %s\n", input);
        return 0;
    } else {
        printf("0x251e says: Wrong flag! Try harder...\n");
        return 1;
    }
}
