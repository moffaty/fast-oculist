// classifier.js
import * as mobilenet from "@tensorflow-models/mobilenet";
import * as knnClassifier from "@tensorflow-models/knn-classifier";
import * as tf from "@tensorflow/tfjs";

export class ObjectClassifier {
    constructor() {
        this.knn = knnClassifier.create();
        this.featureExtractor = null;
    }

    async init() {
        this.featureExtractor = await mobilenet.load();
        console.log("[Classifier] MobileNet loaded");
        this.loadFromStorage();
    }

    async addExample(imgTensor, label) {
        const activation = this.featureExtractor.infer(imgTensor, "conv_preds");
        this.knn.addExample(activation, label);
        activation.dispose();
        console.log(`[Classifier] Added example to "${label}"`);
        this.saveToStorage();
    }

    async classify(imgTensor) {
        if (this.knn.getNumClasses() === 0) return null;
        const activation = this.featureExtractor.infer(imgTensor, "conv_preds");
        const res = await this.knn.predictClass(activation);
        activation.dispose();
        return res; // res.label, res.confidences
    }

    deleteExample(label, exampleIndex = null) {
        const dataset = this.knn.getClassifierDataset();
        if (!dataset[label]) return false;

        const tensor = dataset[label]; // shape [nExamples, dim]
        const arr = tensor.arraySync();

        if (exampleIndex === null) {
            delete dataset[label];
            console.log(
                `[Classifier] Removed class "${label}" and all examples`
            );
        } else {
            arr.splice(exampleIndex, 1);
            if (arr.length === 0) {
                delete dataset[label];
                console.log(
                    `[Classifier] Removed class "${label}" (last example)`
                );
            } else {
                const newTensor = tf.tensor2d(arr, [arr.length, arr[0].length]);
                dataset[label] = newTensor;
                console.log(
                    `[Classifier] Removed example ${exampleIndex} from "${label}"`
                );
            }
        }
        this.knn.setClassifierDataset(dataset);
        this.saveToStorage();
        return true;
    }

    listClasses() {
        return Object.keys(this.knn.getClassifierDataset());
    }

    saveToStorage() {
        try {
            const dataset = this.knn.getClassifierDataset();
            const serializable = {};
            for (const label in dataset) {
                serializable[label] = dataset[label].arraySync();
            }
            localStorage.setItem("knnClassifier", JSON.stringify(serializable));
        } catch (e) {
            console.warn("[Classifier] Could not save to storage:", e);
        }
    }

    loadFromStorage() {
        const data = localStorage.getItem("knnClassifier");
        if (!data) return;
        try {
            const obj = JSON.parse(data);
            const dataset = {};
            for (const label in obj) {
                const arr = obj[label];
                dataset[label] = tf.tensor2d(arr, [arr.length, arr[0].length]);
            }
            this.knn.setClassifierDataset(dataset);
            console.log("[Classifier] Loaded dataset:", Object.keys(obj));
        } catch (e) {
            console.warn("[Classifier] Could not load dataset:", e);
        }
    }
}
