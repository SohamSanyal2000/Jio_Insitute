# K-means-clustering-using-map-reduce-only

Dataset
The data consists of 3 columns which are: 
Customer Id
Income 
Age

K - Means
Parameters:
Set Value of K = 5
No. of iterations = 30

Steps to be followed:
Step1:
Normalize the data Columns using the formula below min-max Normalization over column X:
x = value in column X of a data point
min(x) = minimum value present in Column X max(x) = maximum value present in Column X xl = normalized value of x

Step 2:
Randomly allocate the data points to the clusters.
Then, Calculate the Centroid of each clusters using the formula

Step 3:
Use the Manhattan distance and reassign the clusters to data points.
Datapoints have to be assigned to the nearest clusters based on Manhattan distance.
Recalculate the centroid (New centroid) for each cluster

Step 4:
Repeat Step 3, for 30 times
Calculate the Centroids and reassign the clusters to data points.
Display the Centroids and datapoints assigned to each cluster
