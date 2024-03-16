from transformers import AutoModelForCausalLM, AutoTokenizer
from datetime import datetime
from csv_logger import write_log
import constants


def run(client, ddl, prompts, cache_directory, dataset_name):
    print('*** Query generation statistics: ***')
    print('Client: ' + client)
    print('Model: ' + 'pipSQL')
    print('Dataset: ' + dataset_name)

    pipsql_model_path = 'PipableAI/pip-sql-1.3b'

    if client == constants.CPU:
        model = AutoModelForCausalLM.from_pretrained(pipsql_model_path, cache_dir=cache_directory)
    elif client == constants.GPU_3070:
        model = AutoModelForCausalLM.from_pretrained(pipsql_model_path, cache_dir=cache_directory).to(
            constants.CUDA)
    elif client == constants.GPU_4090:
        model = AutoModelForCausalLM.from_pretrained(pipsql_model_path, cache_dir=cache_directory).to(
            constants.CUDA)

    tokenizer = AutoTokenizer.from_pretrained(pipsql_model_path, cache_dir=cache_directory)

    for i in range(len(prompts)):
        start_time = datetime.now()

        prompt = f"""<schema>{ddl}</schema>
            <question>{prompts[i]}</question>
            <sql>"""

        print('Generating response for prompt ' + str(i + 1) + ': ' + prompts[i])

        if client == constants.CPU:
            inputs = tokenizer(prompt, return_tensors="pt")
        elif client[:3] == 'gpu':
            inputs = tokenizer(prompt, return_tensors="pt").to(constants.CUDA)

        outputs = model.generate(**inputs, max_new_tokens=200)
        response = tokenizer.decode(outputs[0], skip_special_tokens=True).split('<sql>')[1].split('</sql>')[0]

        end_time = datetime.now()
        duration = end_time - start_time

        duration = str(duration.total_seconds())
        print('Elapsed time: ' + duration + ' seconds')
        print('Model response:')
        print(response)
        print('')

        write_log('pipsql_log.csv', 'a', start_time, client, 'pipSQL', dataset_name, i, prompts[i], duration, response)

    print('Done processing dataset ' + dataset_name + ' on pipSQL')
    print('')
