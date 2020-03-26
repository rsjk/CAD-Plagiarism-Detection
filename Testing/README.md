Unit Tests
--
We haven’t done any formal unit testing as of yet, but plan to have several.
We would have 3 different tests which would focus on the bounds of what is and isn’t plagiarism.
The first would provide 2 identical files and check whether or not the application is able to determine this.

Expected: Plagiarism

The second would provide 2 files which are not identical, but would be considered within the bounds of plagiarism as described by our client.

Expected: Plagiarism


The third would provide 2 files which would fall outside of the bounds of plagiarism as described by our client. 

Expected: Not Plagiarism


We could have a test that checks whether or not our installation of the Poppler pdf processing library worked.
This unit test would run our program and then check the environmental PATH variable to see if it contains the path to the Poppler folder and if the folder exists.

Expected: Poppler is in path and on system

System Tests
--
We plan to send our client an executable and have him test that it runs on his system. The only issues we could see popping up is the fact there is a library that we would need to install on the client’s system and add to their “PATH” in order for the program to work, but this will hopefully be handled by the program.

Acceptance Tests
--
We didn’t make formal acceptance tests, but our client told us his acceptance criteria. He provided us with CAD files to test our plagiarism detection program. After trying three different methods to detect plagiarism, we met with our client to discuss the results. He said he preferred the final method of using OpenCV to find contours and compare sub-images of the CAD drawings. He was satisfied with how the contour method detected all instances of plagiarism. The contour method does flag some non-plagiarized files as plagiarized, but our client said he preferred having a few false flags rather than not catching some types of plagiarism. Contour finding was the only method to detect all plagiarism, so we decided to choose it.
