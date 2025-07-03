# https://www.supplycode.dev/posts/fish-shell-script-to-source-enviorment-variables-from-an-env-file
function load_env_vars -d "Load variables in a .env file"
    echo "Loading environment variables from $argv"
    if not test -f $argv
        echo "File not found: $argv"
        return 1
    end
    set lines (cat $argv | string split -n '\n' | string match -vre '^#')
    for line in $lines
        set arr (string split -n -m 1 = $line)
        if test (count $arr) -ne 2
            continue
        end
        set -gx $arr[1] $arr[2]
    end
    echo "Environment variables loaded."
end
