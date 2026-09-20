import os
import pandas as pd
import torch
import time
import matplotlib.pyplot as plt
import seaborn as sns
from coma.dataset import TrainingSmilesDataset, ValidationSmilesDataset
from new_script.Attention_VAE import SmilesAutoencoder, RewardFunction
from coma.properties import qed, penalized_logp, similarity
use_cuda = torch.cuda.is_available()
device = torch.device("cuda:0" if use_cuda else "cpu")
print(device)
# import networkx as nx
from rdkit.Chem import AllChem, GraphDescriptors, Descriptors
from rdkit.Chem import rdMolDescriptors
import imp
import networkx as nx
import numpy as np
from numpy.core.umath_tests import inner1d

from rdkit import Chem
from rdkit.Chem import Descriptors, rdFMCS
from rdkit.DataStructs import TanimotoSimilarity
from rdkit.Chem.AllChem import GetMorganFingerprintAsBitVect
import rdkit.Chem.QED as QED

import coma.sascorer as sascorer

import networkx as nx
from rdkit.Chem import AllChem, GraphDescriptors, Descriptors
from rdkit.Chem import rdMolDescriptors
import imp
import numpy as np
from numpy.core.umath_tests import inner1d

from rdkit import Chem
from rdkit.Chem import Descriptors, rdFMCS
from rdkit.DataStructs import TanimotoSimilarity
from rdkit.Chem.AllChem import GetMorganFingerprintAsBitVect
import rdkit.Chem.QED as QED

import coma.sascorer as sascorer

def penalized_personal(s):
    def has_pyridine_fragments(mol):
        """Проверяет наличие пиридиновых фрагментов и заряженных пиридинов с использованием SMILES."""
        if mol is None:
            return False, False, False, 0
        
        # Паттерны в формате SMILES с заглавными буквами
        patterns = {
            'neutral_pyridine': Chem.MolFromSmiles('C1=CC=NC=C1'),  # Нейтральный пиридин
            'charged_pyridine': Chem.MolFromSmiles('[N+]1=CC=CC=C1'),  # Заряженный пиридин (N+)
            'quinoline': Chem.MolFromSmiles('C1=CC2=C(C=CC=C2)N=C1'),  # Хинолин
            'isoquinoline': Chem.MolFromSmiles('C1=CC2=C(C=CN=C2)C=C1'),  # Изохинолин
            'charged_quinoline': Chem.MolFromSmiles('[N+]1=CC2=C(C=CC=C2)C=C1'),  # Заряженный хинолин
        }
        
        # Считаем количество заряженных ароматических N-гетероциклов
        charged_heterocycles_count = 0
        
        # Проверяем заряженные формы
        if patterns['charged_pyridine'] and mol.HasSubstructMatch(patterns['charged_pyridine']):
            charged_heterocycles_count += len(mol.GetSubstructMatches(patterns['charged_pyridine']))
        
        if patterns['charged_quinoline'] and mol.HasSubstructMatch(patterns['charged_quinoline']):
            charged_heterocycles_count += len(mol.GetSubstructMatches(patterns['charged_quinoline']))
        
        # Проверяем нейтральные формы
        has_neutral_pyridine = False
        if patterns['neutral_pyridine'] and mol.HasSubstructMatch(patterns['neutral_pyridine']):
            has_neutral_pyridine = True
        
        has_charged_pyridine = charged_heterocycles_count > 0
        
        # Проверяем наличие галогенов с отрицательным зарядом как противоионов
        halogen_counterion_patterns = [
            Chem.MolFromSmiles('[Cl-]'),
            Chem.MolFromSmiles('[Br-]'),
            Chem.MolFromSmiles('[I-]')
        ]
        
        has_halogen_counterion = False
        for pattern in halogen_counterion_patterns:
            if pattern and mol.HasSubstructMatch(pattern):
                has_halogen_counterion = True
                break
        
        return has_neutral_pyridine, has_charged_pyridine, has_halogen_counterion, charged_heterocycles_count
    
    def has_long_aliphatic_chain_from_nitrogen(mol, min_chain_length=6):
        """Проверяет наличие длинных алифатических хвостов, связанных с атомами азота в ароматических кольцах."""
        if mol is None:
            return False, False
        
        # Находим все атомы азота в молекуле
        nitrogen_atoms = [atom for atom in mol.GetAtoms() if atom.GetSymbol() == 'N']
        
        if not nitrogen_atoms:
            return False, False
        
        has_long_chain_from_n = False
        has_long_chain_attached = False
        
        for n_atom in nitrogen_atoms:
            n_idx = n_atom.GetIdx()
            
            # Проверяем, находится ли азот в ароматическом кольце
            is_in_aromatic_ring = False
            ring_info = mol.GetRingInfo()
            for ring in ring_info.AtomRings():
                if n_idx in ring:
                    # Проверяем, является ли кольцо ароматическим
                    if all(mol.GetAtomWithIdx(idx).GetIsAromatic() for idx in ring):
                        is_in_aromatic_ring = True
                        break
            
            if not is_in_aromatic_ring:
                continue
            
            # Проверяем соседей азота
            for neighbor in n_atom.GetNeighbors():
                if neighbor.GetSymbol() == 'C' and not neighbor.GetIsAromatic():
                    # Начинаем поиск цепи от соседа азота
                    start_idx = neighbor.GetIdx()
                    
                    # Ищем самую длинную неразветвленную алифатическую цепь
                    max_chain_length = 0
                    visited = set()
                    
                    def dfs(atom_idx, current_length, parent_idx=None):
                        nonlocal max_chain_length
                        if atom_idx in visited:
                            return
                        visited.add(atom_idx)
                        
                        atom = mol.GetAtomWithIdx(atom_idx)
                        # Проверяем, что атом алифатический углерод
                        if atom.GetSymbol() != 'C' or atom.GetIsAromatic():
                            return
                        
                        current_length += 1
                        max_chain_length = max(max_chain_length, current_length)
                        
                        # Получаем соседей (только алифатические углероды)
                        neighbors = []
                        for neighbor_atom in mol.GetAtomWithIdx(atom_idx).GetNeighbors():
                            n_idx_local = neighbor_atom.GetIdx()
                            if (n_idx_local != parent_idx and 
                                neighbor_atom.GetSymbol() == 'C' and 
                                not neighbor_atom.GetIsAromatic() and
                                len(neighbor_atom.GetNeighbors()) <= 2):  # Неразветвленная цепь
                                neighbors.append(n_idx_local)
                        
                        for n_idx_local in neighbors:
                            dfs(n_idx_local, current_length, atom_idx)
                    
                    dfs(start_idx, 0)
                    
                    if max_chain_length >= min_chain_length:
                        has_long_chain_from_n = True
        
        # Также проверяем наличие длинных цепей, прикрепленных к кольцам (но не к N)
        ring_atoms = set()
        for ring in mol.GetRingInfo().AtomRings():
            if len(ring) == 6 and all(mol.GetAtomWithIdx(idx).GetIsAromatic() for idx in ring):
                ring_atoms.update(ring)
        
        for atom_idx in ring_atoms:
            atom = mol.GetAtomWithIdx(atom_idx)
            if atom.GetSymbol() == 'C' and atom.GetIsAromatic():
                for neighbor in atom.GetNeighbors():
                    if neighbor.GetSymbol() == 'C' and not neighbor.GetIsAromatic():
                        start_idx = neighbor.GetIdx()
                        
                        max_chain_length = 0
                        visited = set()
                        
                        def dfs_ring(atom_idx, current_length, parent_idx=None):
                            nonlocal max_chain_length
                            if atom_idx in visited:
                                return
                            visited.add(atom_idx)
                            
                            atom = mol.GetAtomWithIdx(atom_idx)
                            if atom.GetSymbol() != 'C' or atom.GetIsAromatic():
                                return
                            
                            current_length += 1
                            max_chain_length = max(max_chain_length, current_length)
                            
                            neighbors = []
                            for neighbor_atom in mol.GetAtomWithIdx(atom_idx).GetNeighbors():
                                n_idx_local = neighbor_atom.GetIdx()
                                if (n_idx_local != parent_idx and 
                                    neighbor_atom.GetSymbol() == 'C' and 
                                    not neighbor_atom.GetIsAromatic() and
                                    len(neighbor_atom.GetNeighbors()) <= 2):
                                    neighbors.append(n_idx_local)
                            
                            for n_idx_local in neighbors:
                                dfs_ring(n_idx_local, current_length, atom_idx)
                        
                        dfs_ring(start_idx, 0)
                        
                        if max_chain_length >= min_chain_length:
                            has_long_chain_attached = True
        
        return has_long_chain_from_n, has_long_chain_attached
    
    if s is None: 
        return -100.0
    
    # Преобразуем SMILES в верхний регистр для соответствия датасету
    s_upper = s.upper()
    
    mol = Chem.MolFromSmiles(s_upper)
    if mol is None: 
        return -10.0
    
    # Проверяем наличие пиридиновых фрагментов и заряженных гетероциклов
    neutral_pyridine, charged_pyridine, has_halogen_counterion, charged_heterocycles_count = has_pyridine_fragments(mol)
    
    # Проверяем наличие длинных алифатических хвостов от азота
    has_long_chain_from_n, has_long_chain_attached = has_long_aliphatic_chain_from_nitrogen(mol, min_chain_length=6)
    
    # Базовые проверки для заряженных систем
    if charged_pyridine and not has_halogen_counterion:
        # Заряженный пиридин должен иметь противоион
        return -10.0
    
    # Если нет ни одного ароматического N-гетероцикла, штрафуем
    if not neutral_pyridine and charged_heterocycles_count == 0:
        return -10.0
    
    # Вычисляем дескрипторы молекулы
    ring_info = mol.GetRingInfo()
    
    aromatic_cycles = sum(
        all(mol.GetAtomWithIdx(idx).GetIsAromatic() for idx in ring)
        for ring in ring_info.AtomRings()
    )
    
    aliphatic_cycles = sum(
        len(ring) >= 3 and not all(mol.GetAtomWithIdx(idx).GetIsAromatic() for idx in ring)
        for ring in ring_info.AtomRings()
    )
    
    # Система наград и штрафов
    pyridine_reward = 0
    chain_reward = 0
    counterion_reward = 0
    multi_charged_reward = 0
    
    # Награда за заряженные гетероциклы с противоионами
    if charged_pyridine and has_halogen_counterion:
        pyridine_reward += 50.0
        counterion_reward += 15.0  # Увеличенная награда за противоион
    
    # Дополнительная награда за два или более заряженных гетероцикла
    if charged_heterocycles_count >= 2:
        multi_charged_reward += 30.0
    
    # Награда за длинные алифатические хвосты, связанные с азотом в кольцах
    if has_long_chain_from_n:
        chain_reward += 40.0  # Максимальная награда для цепей от азота
    
    # Награда за длинные алифатические хвосты, прикрепленные к кольцу (но не к N)
    if has_long_chain_attached:
        chain_reward += 20.0
    
    # Базовые параметры для нормализации
    logP_mean = 2.4570953396190123
    logP_std = 1.434324401111988
    SA_mean = -1.86
    SA_std = 0.47
    cycle_mean = -0.0485696876403053
    cycle_std = 0.2860212110245455
    Bertz_mean = 1152.12
    Bertz_std = 843.04
    
    # Вычисляем дескрипторы
    bertz = GraphDescriptors.BertzCT(mol)
    log_p = Descriptors.MolLogP(mol)
    SA = -sascorer.calculateScore(mol)
    
    # Cycle score
    cycle_list = nx.cycle_basis(nx.Graph(Chem.rdmolops.GetAdjacencyMatrix(mol)))
    cycle_length = max([len(j) for j in cycle_list]) if len(cycle_list) > 0 else 0
    cycle_score = 0
    if cycle_length not in (0, 5, 6):
        cycle_score += -10
    
    # Нормализуем дескрипторы
    normalized_bertz = (bertz - Bertz_mean) / Bertz_std
    normalized_log_p = (log_p - logP_mean) / logP_std
    normalized_SA = (SA - SA_mean) / SA_std
    normalized_cycle = (cycle_score - cycle_mean) / cycle_std
    
    # Базовая награда за дескрипторы
    base_reward = (
        2.5 * normalized_log_p +    # Повышенный вес для липофильности (важно для хвостов)
        1.0 * normalized_bertz +    # Комплексность молекулы
        1.5 * normalized_SA +       # Синтетическая доступность
        0.8 * normalized_cycle      # Каркас молекулы
    )
    
    # Финальная награда с фокусом на пиридине
    final_reward = (
        base_reward + 
        pyridine_reward + 
        chain_reward + 
        counterion_reward + 
        multi_charged_reward
    )
    
    # Дополнительные штрафы за нежелательные свойства
    if log_p > 9.0:  # Слишком высокая липофильность
        final_reward -= 25.0
    
    if SA < 3.5:  # Слишком сложная синтезируемость
        final_reward -= 20.0
    
    # Бонус за оптимальные свойства
    if 3.0 <= log_p <= 7.0:  # Оптимальная липофильность
        final_reward += 10.0
    
    if has_halogen_counterion and charged_heterocycles_count >= 2:
        final_reward += 25.0  # Большой бонус за двухзарядную систему с противоионами
    
    # Максимальная награда ограничена для стабильности
    return min(final_reward, 150.0)

PROPERTY_NAME = "qed"
# SCORING_PROPERTY_FT = penalized_logp
# threshold_property = 0.
# threshold_similarity = 0.3

PROPERTY_NAME_2 = "personal"
SCORING_PROPERTY_FT = penalized_personal
threshold_property = 0.3
threshold_similarity = 0.3
SCORING_TANIMOTO_FT = similarity
input_data_dir = os.path.abspath(os.path.join(os.pardir, "data", PROPERTY_NAME))
input_ckpt_dir = f"outputs_1_pretraining_Attention_{PROPERTY_NAME}"

filepath_train             = '/home/ilin/COMA/data/qed_Veresh/triplet_rl_3.txt'
filepath_valid             = '/home/ilin/COMA/data/qed_Veresh/valid.txt'
filepath_pretrain_ckpt     = os.path.join(input_ckpt_dir, "checkpoints.pt")
filepath_pretrain_configs  = os.path.join(input_ckpt_dir, "configs.csv")
filepath_pretrain_char2idx = os.path.join(input_ckpt_dir, "char2idx.csv")

output_dir = f"outputs_2_finetuning_Attention_{PROPERTY_NAME_2}"
if not os.path.exists(output_dir):
    os.mkdir(output_dir)

filepath_char2idx      = os.path.join(output_dir, "char2idx.csv")
filepath_configs       = os.path.join(output_dir, "configs.csv")
filepath_checkpoint    = os.path.join(output_dir, "checkpoints.pt")
filepath_history       = os.path.join(output_dir, "history.csv")
filepath_history_valid = os.path.join(output_dir, "history_valid.csv")

dataset = TrainingSmilesDataset(filepath_train, filepath_char2idx=filepath_pretrain_char2idx, device=device)
dataset.save_char2idx(filepath_char2idx)
dataset_valid = ValidationSmilesDataset(filepath_valid, filepath_char2idx, device=device)
## Model configuration
model_configs = {"hidden_size"    :None,
                 "latent_size"    :None,
                 "num_layers"     :None,
                 "vocab_size"     :None,
                 "sos_idx"        :None,
                 "eos_idx"        :None,
                 "pad_idx"        :None,
                 "device"         :device,
                 "filepath_config":filepath_pretrain_configs}

## Model initialization
generator = SmilesAutoencoder(**model_configs)

## Load pretrained model
generator.load_model(filepath_pretrain_ckpt)

## Configuration save
generator.save_config(filepath_configs)
reward_ft = RewardFunction(similarity_ft=SCORING_TANIMOTO_FT,
                           scoring_ft=SCORING_PROPERTY_FT,
                           threshold_property=threshold_property,
                           threshold_similarity=threshold_similarity)
print('We are starting RL')
df_history, df_history_valid = generator.policy_gradient(dataset, reward_ft, validation_dataset=dataset_valid,
                                                         batch_size=1000, total_steps=500, learning_rate=1e-4,
                                                         discount_factor=0.995, buffer_size=2000, buffer_batch_size=50,
                                                         checkpoint_step=50, checkpoint_filepath=filepath_checkpoint,
                                                         display_step=10, verbose=1)
df_history.to_csv(filepath_history, index=False)
df_history_valid.to_csv(filepath_history_valid, index=False)