#!/bin/bash -e

# Notes importantes : la transmission de valeurs de retours via un un variable=$(function) avec function qui renvoie qqchose via echo neutralise la poursuite du script
# En fait le script s'attend à ce que le subshell termine pour passer à l'affectation de variable
# Il va donc falloir adopter deux stratégies de programmation. Une pour lancer / stopper les serveurs dans récupération d'information. L'autre pour contrôler l'état des serveurs
# avec transmission d'information.
# TO BE CONTINUED. ....




available_servers=("apache" "mariadb" "nodejs" "flask")
available_commands=("start" "stop" "restart" "status" "test")

apache_start(){
    service apache2 start &
}

apache_stop(){ 
    service apache2 stop &
}

apache_test(){
    service apache2 restart &
}

apache_status(){
    status=$(service apache2 status)
    if [[ $status =~ "not" ]]; then
        echo "stopped"
    elif [[ $status =~ "running" ]]; then
        echo "started"
    else
        echo "another status : $status"
    fi
}

to_do(){
    $1_$2 #Attention la transmission de paramètres a été désactivée
}

check_args(){
    args=("$@")
    if [ ${#args[@]} != 2 ]; then
        echo "Le script a besoin de deux arguments : un serveur et une action" >&2
        exit 1
    elif [[ ! "${available_servers[@]}" =~ "$1" ]]; then
        echo "Le serveur n'a pas été reconnu." >&2
        exit 1
    elif [[ ! "${available_commands[@]}" =~ "$2" ]]; then
        echo "La commande n'a pas été reconnue." >&2
        exit 1
    fi
    return 0
}

main(){
    check_args $@
    to_do $@
}

main $@
exit $?