# Herschel-summary
A compilation of getting Herschel data of VFS galaxies and analysis of those data

First and foremost, please download the galaxy data and necessary tables to run the codes https://drive.google.com/drive/folders/1lt-3cemwr4ZeUCYj1fII6oPsUf2iM0w6?usp=sharing

The "HTML website generation" Notebook extracts png cutouts of the galaxies in the optical via the legacy survey, as well as write the general home html with the list of galaxies, alongside their cutouts.

The "Masking" notebook first finds the central pixel of the galaxies by converting the central RA & Dec into pixel coordinates inside the Herschel images, then imposes the masks onto it by lining up the central pixels

The "Photometry and individual html file" notebook calculates the photometry of the galaxy in all 6 ellipses, and then outputs those flux measurements into a separate table. The code to calculate photometry takes quite a while to run, but a way to optimize it would be to do something to calculate the images brightness percentages faster. There is also an unfinished code to generate a profile using the 6 ellipses, so more work can be done there. And lastly, there is a code block to generate individual HTML files for all the galaxies

The "CIGALE inputs text file" notebook generates a text file used for CIGALE input. And it does so by compiling all of the fluxes with the necessary specifications. Most notably getting the uncertainties, and adding extinction. Once that's compiled, it outputs it into a txt file in the correct format for CIGALE.

And finally, the "CIGALE Output Sciencing" is the notebook where I take CIGALE outputs, and perform the Dust-to-Gas conversion with it. Then, I extract the combined gas mass from the VFS, and made a series of plots to compare the two.
