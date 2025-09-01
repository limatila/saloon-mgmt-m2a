def generate_dynamic_urls(prefix: str, modules_list: list[str]) -> list[dict[str, str | dict[str, str]]]:    
    modules_list = list(map(lambda module_name: "tipo_servicos" if module_name == "servicos" else module_name, modules_list))
    
    return [
        {
            'name': (
                module_name.lower()
                    .replace('servicos', 'serviços')
                    .title() 
                    .replace("_", " de ")
            ),
            'url_names': {
                'Listar': f'{prefix}:{module_name}:list',
                # 'Cadastro': f'{prefix}:{module_name}:create',
                # 'Modificar': f'{prefix}:{module_name}:update',
                # 'Histórico': f'{prefix}:{module_name}:history'
                #TODO: finish other view types
            }
        }  
        for module_name in modules_list
    ]
