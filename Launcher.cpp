#include <windows.h>
#include <cstdlib>
#include <iostream>
#include <string>

int main() {
    std::cout << "Installing D2SKINCH" << std::endl;
    char path[MAX_PATH];
    GetModuleFileNameA(NULL, path, MAX_PATH);
    std::string exePath(path);
    std::string dir = exePath.substr(0, exePath.find_last_of("\\/"));

    std::string cmd = "python \"" + dir + "\\D2SCCore.exe\"";
    int result = std::system(cmd.c_str());

    if (result != 0) {
        std::cout << "Error: failed to run launcher! (code " << result << ")" << std::endl;
        std::system("pause");
        return 1;
    }
    return 0;
}
