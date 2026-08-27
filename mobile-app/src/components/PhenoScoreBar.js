// High-contrast tactile 0-4 score buttons for rapid field data entry
import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';

export const PhenoScoreBar = ({ label, value = 0, onChange, color = '#2e7d32', icon = '' }) => {
  const scores = [0, 1, 2, 3, 4];

  return (
    <View style={styles.container}>
      <View style={styles.headerRow}>
        <Text style={styles.label}>
          {icon} {label}
        </Text>
        <Text style={[styles.activeValueText, { color }]}>
          {value === 0 ? 'Ausente (0)' : `Nivel ${value} (${value * 25}%)`}
        </Text>
      </View>

      <View style={styles.pillsRow}>
        {scores.map((score) => {
          const isSelected = value === score;
          return (
            <TouchableOpacity
              key={score}
              activeOpacity={0.7}
              onPress={() => onChange(score)}
              style={[
                styles.pillButton,
                isSelected && { backgroundColor: color, borderColor: color },
              ]}
            >
              <Text
                style={[
                  styles.pillText,
                  isSelected && styles.pillTextSelected,
                ]}
              >
                {score}
              </Text>
            </TouchableOpacity>
          );
        })}
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    marginVertical: 6,
    paddingVertical: 4,
  },
  headerRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 6,
  },
  label: {
    fontSize: 14,
    fontWeight: '700',
    color: '#1c3127',
  },
  activeValueText: {
    fontSize: 12,
    fontWeight: '700',
  },
  pillsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  pillButton: {
    flex: 1,
    height: 44, // Altura táctil generosa para dedos con barro o sudor
    marginHorizontal: 3,
    borderRadius: 8,
    borderWidth: 1.5,
    borderColor: '#cfd8dc',
    backgroundColor: '#f8fafc',
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 1,
    elevation: 1,
  },
  pillText: {
    fontSize: 16,
    fontWeight: '800',
    color: '#475569',
  },
  pillTextSelected: {
    color: '#ffffff',
  },
});
